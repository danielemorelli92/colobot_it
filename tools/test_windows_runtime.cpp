// Console-only checks for the portable Windows package; no graphics driver needed.
#define SDL_MAIN_HANDLED
#include <SDL.h>
#include <SDL_image.h>
#include <SDL_ttf.h>
#include <libintl.h>
#include <clocale>
#include <cstdlib>
#include <filesystem>
#include <iostream>
#include <stdexcept>
#include <string>

void Check(bool condition, const std::string& message)
{
    if (!condition) throw std::runtime_error(message);
}

int main(int argc, char** argv)
{
    try
    {
        Check(argc == 2, "Pass the portable package directory");
        const auto root = std::filesystem::absolute(argv[1]);
        static char language[] = "LANGUAGE=it_IT.utf8";
        Check(putenv(language) == 0, "Could not set LANGUAGE");
        Check(std::setlocale(LC_ALL, "") != nullptr, "Default system locale unavailable");
        // Match CApplication: gettext uses LANGUAGE even if the locale alias is unavailable.
        std::setlocale(LC_ALL, "it_IT.utf8");
        std::setlocale(LC_NUMERIC, "C");
        bindtextdomain("colobot", (root / "lang").string().c_str());
        bind_textdomain_codeset("colobot", "UTF-8");
        textdomain("colobot");
        Check(std::string(gettext("Missions")) == "Missioni", "Italian interface catalog not loaded");
        Check(std::string(gettext("Colobot rules!")) == "Colobot è fantastico!", "Accented translation mismatch");
        const char* one = "You have to use \"%1$s\" at least once in this exercise (used: %2$d)";
        const char* many = "You have to use \"%1$s\" at least %3$d times in this exercise (used: %2$d)";
        for (unsigned long count : {0, 1, 2, 10})
        {
            const std::string expected = count == 1
                ? "Devi usare \"%1$s\" almeno una volta in questo esercizio (usi: %2$d)"
                : "Devi usare \"%1$s\" almeno %3$d volte in questo esercizio (usi: %2$d)";
            Check(ngettext(one, many, count) == expected, "Italian plural lookup failed");
        }
        SDL_SetMainReady();
        Check(SDL_Init(0) == 0, SDL_GetError());
        Check((IMG_Init(IMG_INIT_PNG) & IMG_INIT_PNG) != 0, IMG_GetError());
        auto* picture = IMG_Load((root / "data/textures/interface/button1.png").string().c_str());
        Check(picture != nullptr, IMG_GetError());
        SDL_FreeSurface(picture);
        Check(TTF_Init() == 0, TTF_GetError());
        auto* font = TTF_OpenFont((root / "data/fonts/dvu_sans.ttf").string().c_str(), 16);
        Check(font != nullptr, TTF_GetError());
        Check(TTF_GlyphIsProvided(font, 0x00e8) != 0 && TTF_GlyphIsProvided(font, 0x00f9) != 0, "Italian accent glyphs missing");
        TTF_CloseFont(font);
        TTF_Quit();
        IMG_Quit();
        SDL_Quit();
        std::cout << "PASS: portable DLLs, Italian catalog, accents, plurals, PNG images and font loading\n";
        return 0;
    }
    catch (const std::exception& error)
    {
        std::cerr << "FAIL: " << error.what() << '\n';
        return 1;
    }
}
