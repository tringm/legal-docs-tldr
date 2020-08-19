from core.tests.cases import CompareTestCase
from core.data_handler.tosdr import TosdrDataLoader, service_quote_text_and_summary, service_urls


class TestTosdrDataLoader(CompareTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = TosdrDataLoader()
        cls.services_input_folder = cls.input_folder.parent.parent / 'tosdr_services'

    def load_all_services_in_folder_step(self):
        self.loader.load_all_services_data_in_folder(self.services_input_folder)
        self.assertCountEqual(self.loader.loaded_services, ['github', 'nvidia'])

    def force_reload_step(self):
        ori_github_data = self.loader.service_data('github')
        self.loader.load_service_data_in_file(
            self.services_input_folder / 'nvidia.json', service_name='github', force_reload=True
        )
        self.assertDictEqual(self.loader.service_data('nvidia'), self.loader.service_data('github'))
        self.loader.load_service_data_in_file(
            self.services_input_folder / 'github.json', force_reload=True
        )
        self.assertDictEqual(ori_github_data, self.loader.service_data('github'))

    def get_quote_text_and_summary_step(self):
        self.assertCountEqual(
            service_quote_text_and_summary(self.loader.service_data('nvidia')),
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
        self.assertCountEqual(service_urls((self.loader.service_data('nvidia'))), ["nvidia.com", "nvidia.de"])

    def test_step_by_step(self):
        self.load_all_services_in_folder_step()
        self.force_reload_step()
        self.get_quote_text_and_summary_step()
        self.get_urls_step()
