from django.test import TestCase, Client
from django.urls import reverse
from database.models import PesticidalProteinDatabase, Description
from database.filter_results import Search


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.statistics_url = reverse('statistics')
        self.categorize_database_url = reverse(
            'categorize_database', args=['Cry'])
        self.protein_description = Description.objects.create(
            name='Cry',
            description='Mnemonic retained for 3-domain proteins'
        )
        self.protein_example = PesticidalProteinDatabase.objects.create(
            name='Cry1Aa1',
            oldname='Cry1Aa1',
            othernames='Cry1A(a)',
            accession='AAA22353',
            year='1985',
            sequence="""MDNNPNINECIPYNCLSNPEVEVLGGERIETGYTPIDISLSLTQFLLSEFVPGAGFVLGLVDIIWGIFGPSQWDAFPVQIEQLINQRIEEFARNQAISRLEGLSNLYQIYAESFREWEADPTNPALREEMRIQFNDMNSALTTAIPLLAVQNYQVPLLSVYVQAANLHLSVLRDVSVFGQRWGFDAATINSRYNDLTRLIGNYTDYAVRWYNTGLERVWGPDSRDWVRYNQFRRELTLTVLDIVALFSNYDSRRYPIRTVSQLTREIYTNPVLENFDGSFRGMAQRIEQNIRQPHLMDILNSITIYTDVHRGFNYWSGHQITASPVGFSGPEFAFPLFGNAGNAAPPVLVSLTGLGIFRTLSSPLYRRIILGSGPNNQELFVLDGTEFSFASLTTNLPSTIYRQRGTVDSLDVIPPQDNSVPPRAGFSHRLSHVTMLSQAAGAVYTLRAPTFSWQHRSAEFNNIIPSSQITQIPLTKSTNLGSGTSVVKGPGFTGGDILRRTSPGQISTLRVNITAPLSQRYRVRIRYASTTNLQFHTSIDGRPINQGNFSATMSSGSNLQSGSFRTVGFTTPFNFSNGSSVFTLSAHVFNSGNEVYIDRIEFVPAEVTFEAEYDLERAQKAVNELFTSSNQIGLKTDVTDYHIDQVSNLVECLSDEFCLDEKQELSEKVKHAKRLSDERNLLQDPNFRGINRQLDRGWRGSTDITIQGGDDVFKENYVTLLGTFDECYPTYLYQKIDESKLKAYTRYQLRGYIEDSQDLEIYLIRYNAKHETVNVPGTGSLWPLSAQSPIGKCGEPNRCAPHLEWNPDLDCSCRDGEKCAHHSHHFSLDIDVGCTDLNEDLGVWVIFKIKTQDGHARLGNLEFLEEKPLVGEALARVKRAEKKWRDKREKLEWETNIVYKEAKESVDALFVNSQYDQLQADTNIAMIHAADKRVHSIREAYLPELSVIPGVNAAIFEELEGRIFTAFSLYDARNVIKNGDFNNGLSCWNVKGHVDVEEQNNQRSVLVLPEWEAEVSQEVRVCPGRGYILRVTAYKEGYGEGCVTIHEIENNTDELKFSNCVEEEIYPNNTVTCNDYTVNQEEYGGAYTSRNRGYNEAPSVPADYASVYEEKSYTDGRRENPCEFNRGYRDYTPLPVGYVTKELEYFPETDKVWIEIGETEGTFIVDSVELLLMEE"""
        )

    def test_categorize_database(self):

        response = self.client.get(self.categorize_database_url)
        print("response", response.status_code)

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'newwebpage/category_display.html')


class SearchTestCase(TestCase):
    def test_is_full_name(self):
        self.assertEquals(Search('Cry1Aa1').is_fullname(), True)

    def test_is_uppercase(self):
        self.assertEquals(Search('Cry1A').is_uppercase(), True)

    def test_is_lowercase(self):
        self.assertEquals(Search('Cry1Aa').is_lowercase(), True)

    def test_is_single_digit(self):
        self.assertEquals(Search('Cry1').is_single_digit(), True)

    def test_is_double_digit(self):
        self.assertEquals(Search('Cry10').is_double_digit(), True)

    def test_is_triple_digit(self):
        self.assertEquals(Search('Cry100').is_triple_digit(), True)

    def test_is_three_letter_case(self):
        boolean = Search('Cry').is_three_letter_case()
        # self.assertEquals(keyword, True)
        self.assertEqual(boolean, True)
        # self.assertFalse(Search.is_three_letter_case('Cr'))

    def test_digit_length(self):
        self.assertEquals(Search('Cry100').digit_length(), 3)

    def test_is_wildcard(self):
        self.assertEquals(Search('Cry1*').is_wildcard(), True)

    def test_fulltext(self):
        self.assertEquals(Search('CGCryV').fulltext(), True)
