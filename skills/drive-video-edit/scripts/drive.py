#!/usr/bin/env python3
"""Memory-only OAuth and create-only Drive video transfer; Python standard library."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

API = 'https://www.googleapis.com/drive/v3/files'
FIELDS = 'id,name,mimeType,size,webViewLink'
CHUNK = 8 * 1024 * 1024  # multiple of 256 KiB


class DriveError(Exception):
    pass


class Drive:
    def __init__(self):
        keys = ('GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REFRESH_TOKEN')
        missing = [k for k in keys if not os.environ.get(k)]
        if missing:
            raise DriveError('Missing network secrets: ' + ', '.join(missing))
        self.private = [os.environ[k] for k in keys]
        self.token = None
        self.refresh()

    def redact(self, text):
        for value in self.private:
            text = text.replace(value, '[REDACTED]')
        return text

    def request(self, url, method='GET', data=None, headers=None, auth=True, allow_resume=False):
        headers = dict(headers or {})
        if auth:
            headers['Authorization'] = 'Bearer ' + self.token
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            return urllib.request.urlopen(req, timeout=120)
        except urllib.error.HTTPError as exc:
            if allow_resume and exc.code == 308:
                return exc
            # Google response body is the exact error, except any credential echoes.
            raise DriveError(self.redact(exc.read().decode('utf-8', 'replace'))) from None
        except urllib.error.URLError as exc:
            raise DriveError(self.redact(str(exc))) from None

    def refresh(self):
        body = urllib.parse.urlencode(dict(zip(
            ('client_id', 'client_secret', 'refresh_token'), self.private[:3]),
            grant_type='refresh_token')).encode()
        with self.request('https://oauth2.googleapis.com/token', 'POST', body,
                          {'Content-Type': 'application/x-www-form-urlencoded'}, auth=False) as r:
            payload = json.load(r)
        self.token = payload.get('access_token')
        if not self.token:
            raise DriveError('Token response did not contain an access_token.')
        self.private.append(self.token)

    def find(self, name=None, file_id=None):
        if file_id:
            url = API + '/' + urllib.parse.quote(file_id, safe='') + '?' + urllib.parse.urlencode({'fields': FIELDS})
            with self.request(url) as r:
                result = json.load(r)
        else:
            escaped = name.replace('\\', '\\\\').replace("'", "\\'")
            query = {'q': "trashed = false and name = '" + escaped + "'",
                     'fields': 'nextPageToken,files(' + FIELDS + ')', 'pageSize': 100}
            with self.request(API + '?' + urllib.parse.urlencode(query)) as r:
                payload = json.load(r)
            matches = payload.get('files', [])
            if not matches:
                raise DriveError('File is not visible with drive.file scope. It likely needs to be opened with the app or uploaded by it; supply an accessible file ID.')
            if len(matches) != 1 or payload.get('nextPageToken'):
                raise DriveError('Multiple files have this name. Supply a file ID; no file was selected.')
            result = matches[0]
        if not result['mimeType'].startswith('video/'):
            raise DriveError('Selected file is not a downloadable video: ' + result['mimeType'])
        return result

    def download(self, file_id, path):
        url = API + '/' + urllib.parse.quote(file_id, safe='') + '?alt=media'
        with self.request(url) as r, path.open('xb') as out:
            while True:
                chunk = r.read(CHUNK)
                if not chunk:
                    break
                out.write(chunk)

    def upload(self, path, name, mime):
        size = path.stat().st_size
        if not size:
            raise DriveError('Edited output is empty.')
        self.refresh()  # Editing may outlive the first token.
        url = 'https://www.googleapis.com/upload/drive/v3/files?' + urllib.parse.urlencode({'uploadType': 'resumable', 'fields': FIELDS})
        with self.request(url, 'POST', json.dumps({'name': name}).encode(), {
                'Content-Type': 'application/json', 'X-Upload-Content-Type': mime,
                'X-Upload-Content-Length': str(size)}) as r:
            session = r.headers['Location']
        # Session URLs are capabilities: keep them in memory and out of errors.
        self.private.append(session)
        parsed = urllib.parse.urlsplit(session)
        if parsed.scheme != 'https' or parsed.hostname != 'www.googleapis.com':
            raise DriveError('Unexpected resumable upload host.')
        with path.open('rb') as source:
            start = 0
            while start < size:
                chunk = source.read(CHUNK)
                end = start + len(chunk) - 1
                try:
                    with self.request(session, 'PUT', chunk, {
                            'Content-Type': mime, 'Content-Length': str(len(chunk)),
                            'Content-Range': f'bytes {start}-{end}/{size}'}, allow_resume=True) as r:
                        if r.code == 308:
                            expected = f'bytes=0-{end}'
                            if r.headers.get('Range') != expected:
                                raise DriveError('Unexpected resumable upload acknowledgement; no retry attempted.')
                            start = end + 1
                            continue
                        result = json.load(r)
                    if end != size - 1:
                        raise DriveError('Upload completed before all bytes were sent.')
                    if not result.get('webViewLink'):
                        raise DriveError('Upload response did not contain webViewLink; do not retry blindly because a file may already exist.')
                    if int(result['size']) != size:
                        raise DriveError('Uploaded size differs from local output.')
                    return result
                except DriveError:
                    raise
                start = end + 1
        raise DriveError('Upload ended without a completion response.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--name')
    group.add_argument('--id')
    parser.add_argument('--ext', required=True, help='Output extension, e.g. mp4')
    parser.add_argument('--mime', required=True, help='Output MIME type, e.g. video/mp4')
    parser.add_argument('editor', nargs=argparse.REMAINDER,
                        help='Command after --; {input} and {output} are substituted')
    args = parser.parse_args()
    editor = args.editor[1:] if args.editor[:1] == ['--'] else args.editor
    if not editor or not any('{output}' in arg for arg in editor):
        parser.error('Editor command must include {output}.')
    if not args.ext.isalnum() or not args.mime.startswith('video/'):
        parser.error('Use an alphanumeric extension and a video MIME type.')
    drive = None
    try:
        drive = Drive()
        metadata = drive.find(args.name, args.id)
        with tempfile.TemporaryDirectory(prefix='drive-video-edit-') as folder:
            root = Path(folder)
            source = root / ('source' + Path(metadata['name']).suffix)
            output = root / ('edited.' + args.ext)
            drive.download(metadata['id'], source)
            if metadata.get('size') and source.stat().st_size != int(metadata['size']):
                raise DriveError('Downloaded size differs from Drive metadata.')
            source.chmod(0o400)
            # Do not pass OAuth secrets to editor subprocesses.
            env = {k: v for k, v in os.environ.items() if k not in (
                'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REFRESH_TOKEN')}
            command = [a.replace('{input}', str(source)).replace('{output}', str(output)) for a in editor]
            subprocess.run(command, check=True, env=env)
            if not output.is_file() or output.is_symlink():
                raise DriveError('Editor did not produce a regular output file.')
            print('Review the local output before upload: ' + str(output), flush=True)
            if input('Confirm requested edits and review passed; upload as a new file? [y/N] ').strip().lower() != 'y':
                print('Upload cancelled; temporary files cleaned up.')
                return
            name = Path(metadata['name']).stem + '-edited.' + args.ext
            result = drive.upload(output, name, args.mime)
            print(json.dumps({k: result[k] for k in ('name', 'size', 'webViewLink')}, ensure_ascii=False))
    except (DriveError, OSError, subprocess.CalledProcessError, ValueError, KeyError, EOFError) as exc:
        print(drive.redact(str(exc)) if drive else str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
