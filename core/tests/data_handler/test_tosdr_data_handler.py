from core.tests.cases import CompareTestCase
from core.data_handler.tosdr import TosdrDataLoader


class TestTosdrDataLoader(CompareTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = TosdrDataLoader()
        cls.services_input_folder = cls.input_folder.parent.parent / 'tosdr_services'

    def load_all_services_in_folder_step(self):
        self.loader.load_all_services_file_in_folder(self.services_input_folder)
        self.assertCountEqual(self.loader.loaded_services, ['github', 'nvidia'])

    def force_reload_step(self):
        ori_github_data = self.loader.service_data('github')
        self.loader.load_service_data_from_file(
            self.services_input_folder / 'nvidia.json', service_name='github', force_reload=True
        )
        self.assertEqual(self.loader.service_data('nvidia').summary_cases, self.loader.service_data('github').summary_cases)
        self.loader.load_service_data_from_file(
            self.services_input_folder / 'github.json', force_reload=True
        )
        self.assertEqual(ori_github_data, self.loader.service_data('github'))

    def get_quote_text_and_summary_step(self):
        self.assertCountEqual(
            self.loader.service_data('nvidia').all_quote_texts_and_summaries,
            [('Right to access. You can see what data we have collected whenever you '
              'want.\n\n'
              'Right to take your data. The data is yours.\n'
              'You can copy or move it whenever you want.\n\n'
              'Right to erasure. We\'ll erase your personal data whenever you say the word.',
              'You can request access and deletion of personal data'),
             ('We never sell your data.', 'This service does not sell your personal data')]
        )

    def test_step_by_step(self):
        self.load_all_services_in_folder_step()
        self.force_reload_step()
        self.get_quote_text_and_summary_step()
