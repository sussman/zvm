#
# Unit and integration tests for the zaudio module.
#
# For the license of this file, please consult the LICENSE file in the
# root directory of this distribution.
#

from unittest import TestCase
import zvm.zaudio
import zvm.trivialzui

def is_function_implemented(function):
    """Returns True if the given function appears to be implemented,
    False if not.  This is actually a fairly brittle test that just
    checks to see if a function consists of a body that raises
    NotImplementedError."""
    
    names = function.func_code.co_names

    # If the only name used by the function is NotImplementedError,
    # then there's a pretty good chance that it's a function that
    # just raises NotImplementedError.

    if names == ('NotImplementedError',):
        return False
    else:
        return True

class AnyZAudioTestsMixIn:
    """Sanity-check tests that can be used on any ZAudio instance.

    This is a mix-in class, intended to be mixed-in with an existing
    subclass of unittest.TestCase.  Subclasses should be sure to set
    up the zaudio attribute of the class to point to a ZAudio
    instance, or else lots of AttributeError exceptions will occur."""

    RECOGNIZED_FEATURES = ["has_more_than_a_bleep"]

    def testZAudioIsZAudioInstance(self):
        assert isinstance(self.zaudio, zvm.zaudio.ZAudio)

    def testAllFeaturesAreRecognized(self):
        for feature_name in self.zaudio.features.keys():
            if feature_name not in self.RECOGNIZED_FEATURES:
                raise AssertionError(
                   "ZAudio instance contains unknown feature '%s'" % \
                   feature_name
                   )

    def testAllRecognizedFeaturesAreSpecified(self):
        for feature_name in self.RECOGNIZED_FEATURES:
            if not self.zaudio.features.has_key(feature_name):
                raise AssertionError(
                    "ZAudio instance does not specify whether it " \
                    "supports feature '%s'" % feature_name
                    )

    def testHasMoreThanABleepFeatureIsSane(self):
        if not self.zaudio.features["has_more_than_a_bleep"]:
            self.assertRaises(
                NotImplementedError,
                self.zaudio.play_sound_effect,
                0, 0, 0, 0, 0
                )
        else:
            assert is_function_implemented(self.zaudio.play_sound_effect), \
                   "Method play_sound_effect() must be implemented."

class TrivialAudioTests(TestCase, AnyZAudioTestsMixIn):
    def setUp(self):
        self.zaudio = zvm.trivialzui.TrivialAudio()
