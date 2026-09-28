import unittest

from app import app


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Smart Keyboard", response.data)

    def test_predict_returns_suggestions(self):
        response = self.client.post("/predict", json={"text": "I want to"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["suggestions"])

    def test_autocorrect_preserves_punctuation(self):
        response = self.client.post("/autocorrect", json={"text": "Teh, world!"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["corrected"], "The, world!")

    def test_api_rejects_non_string_text(self):
        self.assertEqual(self.client.post("/predict", json={"text": 42}).status_code, 400)
        self.assertEqual(self.client.post("/autocorrect", json={"text": []}).status_code, 400)

    def test_overview_reports_real_corpus_diagnostic(self):
        response = self.client.get("/api/overview")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertGreater(data["corpus_words"], 0)
        self.assertGreater(data["evaluation"]["held_out_sentences"], 0)
        self.assertLessEqual(data["evaluation"]["top_5_accuracy"], 1)

    def test_autocorrect_returns_adjusted_cursor(self):
        response = self.client.post("/autocorrect", json={"text": "Teh, world!", "cursor": 4})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["corrected"], "The, world!")
        self.assertEqual(response.get_json()["cursor"], 4)

    def test_rejects_invalid_cursor_and_large_input(self):
        self.assertEqual(
            self.client.post("/autocorrect", json={"text": "hello", "cursor": True}).status_code,
            400,
        )
        self.assertEqual(
            self.client.post("/predict", json={"text": "x" * 10001}).status_code,
            413,
        )


if __name__ == "__main__":
    unittest.main()
