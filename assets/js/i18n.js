function createLanguageSelect(currentLanguage, defaultLanguage) {
    // https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes
    // FIXME: This should be a separate function that fetches a json file
    const availableLanguages = [
        {
            language: "Eesti keel",
            languageCode: "et",
        },
    ];
    availableLanguages.push(defaultLanguage);

    const element = `
    <ul class="navbar-nav ms-auto">
        <li class="nav-item dropdown pt-2 pb-2 fw-semibold">
            <a class="d-inline nav-link dropdown-toggle pe-0" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="d-inline fa fa-language" aria-hidden="true"></i>
                <span id="current-language" class="ms-1">${currentLanguage["language"]} (${currentLanguage["languageCode"]})</span>
            </a>
            <ul id="languageSelectDropdown" class="dropdown-menu">
            </ul>
        </li>
    </ul>
    `;

    const navbarElement = document.querySelector("#navbarNav");
    navbarElement.insertAdjacentHTML("beforeend", element);

    const languageSelectDropdown = document.querySelector(
        "#languageSelectDropdown",
    );

    availableLanguages.forEach((language) => {
        if (language["language"] === currentLanguage["language"]) {
            return;
        }

        childElement = `
        <li>
            <a class="dropdown-item fw-semibold"
                onclick="setCurrentLanguage(&quot;${language["language"]}&quot;, &quot;${language["languageCode"]}&quot;);"
                href="#">${language["language"]} (${language["languageCode"]})</a>
        </li>
        `;
        languageSelectDropdown.insertAdjacentHTML("afterbegin", childElement);
    });
}

async function fetchLanguageData(languageCode) {
    const response = await fetch(`/assets/languages/${languageCode}.json`);

    if (response.status !== 200) {
        console.error(`Unable to fetch language data for "${languageCode}"`);
        return;
    }

    return response.json();
}

function getPageName() {
    // Create a URL object
    const urlObject = new URL(window.location.href);

    // Get the path from the URL and remove any trailing slashes
    let path = urlObject.pathname.replace(/\/$/, "");

    // If the path ends with "/index.html", remove it
    if (path.endsWith("/index.html")) {
        path = path.replace("/index.html", "");
    } else if (path === "/index.html") {
        return "index"; // Special case for root "/index.html"
    }

    // Split the path into segments
    const segments = path.split("/").filter((segment) => segment !== "");

    // Return "index" if no segments, otherwise return the first segment
    return segments.length === 0 ? "index" : segments[0];
}

function updateContent(languageData) {
    document.querySelectorAll("[data-i18n]").forEach((element) => {
        const key = element.getAttribute("data-i18n");

        if (typeof languageData[key] !== "undefined") {
            console.debug(`Translating: ${key}`);
            element.innerHTML = languageData[key];
        } else {
            console.debug(
                `${key} is missing from language data. Skipping translation.`,
            );
        }
    });
}

function setCurrentLanguage(language, languageCode) {
    localStorage.setItem(
        "language",
        JSON.stringify({
            language: `${language}`,
            languageCode: `${languageCode}`,
        }),
    );

    window.location.reload();
}

// start benchmark
const startTime = performance.now();

document.addEventListener("DOMContentLoaded", async () => {
    const defaultLanguage = {
        language: "English",
        languageCode: "en",
    };

    // get users chosen language or set it to defaultLanguage
    const currentLanguage =
        JSON.parse(localStorage.getItem("language")) || defaultLanguage;

    // create language select nav element
    createLanguageSelect(currentLanguage, defaultLanguage);

    if (currentLanguage["languageCode"] !== defaultLanguage["languageCode"]) {
        const languageData = await fetchLanguageData(
            currentLanguage["languageCode"],
        );

        if (typeof languageData !== "undefined") {
            const pageName = getPageName();

            // translate global content
            updateContent(languageData["globalContent"]);

            // translate page content
            if (typeof languageData["pageContent"][pageName] !== "undefined") {
                updateContent(languageData["pageContent"][pageName]);
            }
        } else {
            console.error(`languageData is undefined. Translation skipped.`);
        }
    }

    // dispatch an event so it's possible to check if the translation is finished
    const event = new Event("i18nFinished");
    document.dispatchEvent(event);

    // end benchmark
    const endTime = performance.now();
    console.debug(`Script execution time took ${endTime - startTime}ms`);
});
