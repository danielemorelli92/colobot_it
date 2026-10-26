#include "common/language.h"
#include <cassert>
#include <string>
int main()
{
    Language lang = LANGUAGE_ENV;
    assert(ParseLanguage("it", lang) && lang == LANGUAGE_ITALIAN);
    std::string code;
    assert(LanguageToString(lang, code) && code == "it");
    for (const auto* existing : {"en", "fr", "de", "pl", "ru", "cs", "pt"})
    {
        assert(ParseLanguage(existing, lang));
        assert(LanguageToString(lang, code) && code == existing);
    }
    assert(!ParseLanguage("xx", lang));
}
