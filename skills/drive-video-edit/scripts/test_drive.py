import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

from drive import Drive, DriveError, CHUNK


class Response(io.BytesIO):
    def __init__(self, data, code=200, headers=None):
        super().__init__(json.dumps(data).encode())
        self.code = code
        self.headers = headers or {}


class TransferTests(unittest.TestCase):
    def client(self):
        d = Drive.__new__(Drive)
        d.private = ['client-secret', 'refresh-secret', 'access-secret']
        d.token = 'access-secret'
        return d

    def test_exact_error_redacts_credentials(self):
        error = urllib.error.HTTPError('https://example.test', 403, 'Forbidden', {},
                                      io.BytesIO(b'{"error":"denied access-secret"}'))
        with patch('urllib.request.urlopen', side_effect=error):
            with self.assertRaisesRegex(DriveError, 'denied \\[REDACTED\\]'):
                self.client().request('https://example.test')

    def test_duplicate_names_are_not_selected(self):
        with patch.object(Drive, 'request', return_value=Response({'files': [{}, {}]})):
            with self.assertRaisesRegex(DriveError, 'Multiple files'):
                self.client().find(name="a'b.mp4")

    def test_invisible_file_explains_scope(self):
        with patch.object(Drive, 'request', return_value=Response({'files': []})):
            with self.assertRaisesRegex(DriveError, 'opened with the app'):
                self.client().find(name='missing.mp4')

    def test_resumable_upload_creates_and_sends_all_chunks(self):
        calls = []
        size = CHUNK + 3
        def respond(url, method='GET', data=None, headers=None, **kwargs):
            calls.append((url, method, headers, len(data)))
            if method == 'POST':
                return Response({}, headers={'Location': 'https://www.googleapis.com/upload/session'})
            if len(calls) == 2:
                return Response({}, code=308, headers={'Range': f'bytes=0-{CHUNK-1}'})
            return Response({'name': 'tour-edited.mp4', 'size': str(size), 'webViewLink': 'https://drive.google.com/view'})
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'out.mp4'
            with output.open('wb') as f:
                f.truncate(size)
            with patch.object(Drive, 'refresh'), patch.object(Drive, 'request', side_effect=respond):
                result = self.client().upload(output, 'tour-edited.mp4', 'video/mp4')
        self.assertEqual(result['size'], str(size))
        self.assertEqual([c[1] for c in calls], ['POST', 'PUT', 'PUT'])
        self.assertEqual(calls[-1][2]['Content-Range'], f'bytes {CHUNK}-{size-1}/{size}')
        self.assertNotIn('/files/', calls[0][0])

    def test_308_is_returned_only_for_upload(self):
        error = urllib.error.HTTPError('https://example.test', 308, 'Resume Incomplete',
                                      {'Range': 'bytes=0-3'}, io.BytesIO(b''))
        with patch('urllib.request.urlopen', side_effect=error):
            self.assertEqual(self.client().request('https://example.test', allow_resume=True).code, 308)


if __name__ == '__main__':
    unittest.main()
