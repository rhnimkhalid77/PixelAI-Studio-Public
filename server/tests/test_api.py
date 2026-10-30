import base64
import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from app import app

client = TestClient(app)
TOKEN = "t" * 40

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"PIXELAI_API_TOKEN": TOKEN}, clear=False)
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_health_is_explicit_about_video_limit(self):
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["video_generation"], "not-implemented")

    def test_requires_server_token(self):
        response = client.post("/v1/generations", json={"prompt": "A cinematic mountain"})
        self.assertEqual(response.status_code, 401)

    def test_video_is_not_falsely_reported_as_generated(self):
        response = client.post(
            "/v1/generations",
            headers={"Authorization": "Bearer " + TOKEN},
            json={"prompt": "A cinematic mountain", "output": "video"},
        )
        self.assertEqual(response.status_code, 501)

    def test_rejects_short_prompt(self):
        response = client.post(
            "/v1/generations",
            headers={"Authorization": "Bearer " + TOKEN},
            json={"prompt": "no"},
        )
        self.assertEqual(response.status_code, 422)

    def test_image_generation_returns_png_payload(self):
        with patch("model_adapter.generate_image", return_value=b"fake-png-bytes") as generate:
            response = client.post(
                "/v1/generations",
                headers={"Authorization": "Bearer " + TOKEN},
                json={"prompt": "A cinematic mountain", "style": "Fantasy", "seed": 7},
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "generated")
        self.assertEqual(response.json()["mime_type"], "image/png")
        self.assertEqual(base64.b64decode(response.json()["image_base64"]), b"fake-png-bytes")
        self.assertIn("Fantasy", generate.call_args.args[0])

if __name__ == "__main__":
    unittest.main()
