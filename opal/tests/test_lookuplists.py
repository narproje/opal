"""
Unittests for opal.core.lookuplists
"""
from opal.core.test import OpalTestCase
from opal.models import Synonym
from opal.tests.models import Hat, EtherialHat, GhostHat
from django.contrib.contenttypes.models import ContentType
from opal.core.lookuplists import load_lookuplist, lookuplists


class AbstractLookupListTestCase(OpalTestCase):
    def setUp(self):
        self.hat = Hat.objects.create(name="Cowboy")
        ct = ContentType.objects.get_for_model(Hat)
        Synonym.objects.create(
            content_type=ct,
            object_id=self.hat.id,
            name="Stetson"
        )


class LookupListLoadingTestCase(AbstractLookupListTestCase):

    def test_create_instance(self):
        data = {"hat": [dict(name="Bowler", synonyms=[])]}
        _, created, _ = load_lookuplist(data)
        self.assertEqual(created, 1)

    def test_dont_create_instance(self):
        data = {"hat": [dict(name="Cowboy", synonyms=[])]}
        _, created, _ = load_lookuplist(data)
        self.assertEqual(created, 0)

    def test_create_synonym(self):
        data = {"hat": [dict(name="Cowboy", synonyms=["Ten Gallon"])]}
        _, created, synonyms = load_lookuplist(data)
        self.assertEqual(created, 0)
        self.assertEqual(synonyms, 1)

    def test_dont_create_synonym(self):
        data = {"hat": [dict(name="Cowboy", synonyms=["Stetson"])]}
        _, created, synonyms = load_lookuplist(data)
        self.assertEqual(created, 0)
        self.assertEqual(synonyms, 0)

    def test_create_instance_and_synonym(self):
        data = {"hat": [dict(name="Bowler", synonyms=["Derby"])]}
        _, created, synonyms = load_lookuplist(data)
        self.assertEqual(created, 1)
        self.assertEqual(synonyms, 1)

    def test_create_instance_allow_no_symptom(self):
        data = {"hat": [dict(name="Bowler")]}
        _, created, synonyms = load_lookuplist(data)
        self.assertEqual(created, 1)
        self.assertEqual(synonyms, 1)


class LookupListClassTestCase(AbstractLookupListTestCase):
    def test_unicode(self):
        self.assertEqual(self.hat.__unicode__(), u"Cowboy")

    def test_to_dict(self):
        self.assertEqual(self.hat.to_dict(self.user), "Cowboy")

    def test_get_api_name(self):
        self.assertEqual(Hat.get_api_name(), "hat")

    def test_save_with_synonym(self):
        with self.assertRaises(ValueError) as v:
            Hat.objects.create(name="Stetson")

    def test_save_normal(self):
        Hat.objects.create(name="Bowler")
        self.assertTrue(Hat.objects.filter(name="Bowler").exists())


class LookuplistsIteratorTestCase(AbstractLookupListTestCase):
    def test_lookuplists(self):
        all_lists = list(lookuplists())
        self.assertIn(Hat, all_lists)

    def test_ignores_abstract(self):
        """
        ignore models where meta.abstract == true
        """
        all_lists = list(lookuplists())
        self.assertNotIn(EtherialHat, all_lists)

    def test_includes_subclasses_of_abstract_lookuplists(self):
        """
        make sure we include things that don't
        directly inherit from lookup lists
        """
        all_lists = list(lookuplists())
        self.assertIn(GhostHat, all_lists)
