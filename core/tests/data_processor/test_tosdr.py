from core.tests.cases import CompareTestCase
from core.data_processor.tosdr import TosdrDataPreprocessor


class TestTosdrDataPreprocessor(CompareTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.processor = TosdrDataPreprocessor()
        cls.services_input_folder = cls.services_folder.parent.parent / 'tosdr_services'

    def load_all_services_in_folder_step(self):
        self.processor.load_all_services_data_in_folder(self.services_input_folder)
        self.assertCountEqual(self.processor.loaded_services, ['github', 'nvidia'])

    def get_quote_text_and_summary_step(self):
        self.assertCountEqual(
            self.processor.service_quote_text_and_summary('nvidia'),
            [('Right to access.</b> You can see what data we have collected whenever you '
              'want.</li>\n'
              '<li>\n'
              '<b>Right to take your data.</b> The data is yours.\n'
              'You can copy or move it whenever you want.</li>\n'
              '<li>\n'
              "<b>Right to erasure.</b> We'll erase your personal data whenever you say "
              'the word.',
              'You can request access and deletion of personal data'),
             ('We never sell your data.', 'This service does not sell your personal data')]
        )

    def get_urls_step(self):
        self.assertCountEqual(self.processor.service_urls('nvidia'), ["nvidia.com", "nvidia.de"])

    def test_processor(self):
        self.load_all_services_in_folder_step()
        self.get_quote_text_and_summary_step()
        self.get_urls_step()
