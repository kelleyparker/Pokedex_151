const searchInput = document.querySelector("#search");
const typeFilter = document.querySelector("#typeFilter");
const versionFilter = document.querySelector("#versionFilter");
const habitatFilter = document.querySelector("#habitatFilter");
const pokemonList = document.querySelector("#pokemonList");
const pokemonDetail = document.querySelector("#pokemonDetail");
const resultsCount = document.querySelector("#resultsCount");

let activePokemonId = 1;
const kantoReferenceData =
  typeof window !== "undefined" && window.kantoReferenceData
    ? window.kantoReferenceData
    : {};

function formatDexNumber(id) {
  return `#${String(id).padStart(3, "0")}`;
}

function artworkPath(id) {
  const padded = String(id).padStart(3, "0");
  return `./assets/official-artwork/${padded}.png`;
}

function fallbackArtworkPath(id) {
  return `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${id}.png`;
}

function uniqueValues(key) {
  return [...new Set(pokemon151.map((entry) => entry[key]).flat())].sort();
}

function createTypePill(type) {
  return `<span class="type-pill" data-type="${type}">${type}</span>`;
}

function getReference(entry) {
  return kantoReferenceData[String(entry.id)] || null;
}

function getVersionFlavorEntries(reference) {
  if (!reference || !reference.pokedexText) {
    return [];
  }

  return ["red", "blue", "yellow"]
    .filter((version) => reference.pokedexText[version])
    .map((version) => ({
      version,
      text: reference.pokedexText[version],
    }));
}

function formatVersionLabel(version) {
  return version.charAt(0).toUpperCase() + version.slice(1);
}

function renderEncounterLocations(reference) {
  if (!reference || !reference.encounterLocations || !reference.encounterLocations.length) {
    return `<p>${reference?.locationFallback || "Not found in the wild in standard Red, Blue, or Yellow play."}</p>`;
  }

  return `
    <ul class="detail__list">
      ${reference.encounterLocations
        .map(
          (location) => `
            <li>
              <strong>${location.versionLabel}:</strong> ${location.locations.join(", ")}
            </li>
          `
        )
        .join("")}
    </ul>
  `;
}

function renderMoveTable(reference) {
  if (!reference || !reference.learnset || !reference.learnset.length) {
    return `<p>No level-up moves are cached yet for this Pokemon.</p>`;
  }

  return `
    <div class="move-table-wrap">
      <table class="move-table">
        <thead>
          <tr>
            <th>Move</th>
            <th>Red/Blue</th>
            <th>Yellow</th>
          </tr>
        </thead>
        <tbody>
          ${reference.learnset
            .map(
              (move) => `
                <tr>
                  <td>${move.move}</td>
                  <td>${move.redBlueLevel}</td>
                  <td>${move.yellowLevel}</td>
                </tr>
              `
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}

function matchesFilters(entry) {
  const query = searchInput.value.trim().toLowerCase();
  const type = typeFilter.value;
  const version = versionFilter.value;
  const habitat = habitatFilter.value;
  const reference = getReference(entry);
  const encounterBlob = reference?.encounterLocations
    ? reference.encounterLocations
        .map((group) => `${group.versionLabel} ${group.locations.join(" ")}`)
        .join(" ")
    : "";
  const flavorBlob = reference?.pokedexText ? Object.values(reference.pokedexText).join(" ") : "";
  const moveBlob = reference?.learnset ? reference.learnset.map((move) => move.move).join(" ") : "";

  const matchesQuery =
    !query ||
    [
      entry.name,
      entry.types.join(" "),
      entry.habitat,
      entry.location,
      entry.role,
      entry.summary,
      encounterBlob,
      flavorBlob,
      moveBlob,
    ]
      .join(" ")
      .toLowerCase()
      .includes(query);

  const matchesType = type === "All" || entry.types.includes(type);
  const matchesVersion = version === "All" || entry.versions.includes(version);
  const matchesHabitat = habitat === "All" || entry.habitat === habitat;

  return matchesQuery && matchesType && matchesVersion && matchesHabitat;
}

function renderList(entries) {
  resultsCount.textContent = `${entries.length} entr${entries.length === 1 ? "y" : "ies"}`;

  if (!entries.length) {
    pokemonList.innerHTML = `
      <div class="empty-state">
        <div>
          <h3>No Pokemon matched the current signal scan.</h3>
          <p>Try a broader search or reset one of the filters.</p>
        </div>
      </div>
    `;
    pokemonDetail.innerHTML = "";
    return;
  }

  if (!entries.find((entry) => entry.id === activePokemonId)) {
    activePokemonId = entries[0].id;
  }

  pokemonList.innerHTML = entries
    .map(
      (entry) => `
        <button class="pokemon-card ${entry.id === activePokemonId ? "is-active" : ""}" data-id="${entry.id}">
          <div class="pokemon-card__top">
            <div>
              <div class="pokemon-card__number">${formatDexNumber(entry.id)}</div>
              <div class="pokemon-card__name">${entry.name}</div>
            </div>
            <img class="pokemon-card__art" src="${artworkPath(entry.id)}" alt="${entry.name} artwork" loading="lazy" onerror="this.onerror=null;this.src='${fallbackArtworkPath(entry.id)}'" />
            <div class="chip-row">
              ${entry.types.map(createTypePill).join("")}
            </div>
          </div>
          <div class="pokemon-card__meta">${entry.location}</div>
        </button>
      `
    )
    .join("");

  renderDetail(entries.find((entry) => entry.id === activePokemonId));
}

function renderDetail(entry) {
  if (!entry) {
    pokemonDetail.innerHTML = "";
    return;
  }

  const reference = getReference(entry);
  const flavorEntries = getVersionFlavorEntries(reference);

  pokemonDetail.innerHTML = `
    <div class="detail__hero">
      <div class="detail__identity">
        <div class="detail__header">
          <div class="detail__number">${formatDexNumber(entry.id)}</div>
          <div class="chip-row">
            <span class="chip">${entry.habitat}</span>
            <span class="chip">${entry.availability}</span>
          </div>
        </div>
        <h2 class="detail__name">${entry.name}</h2>
        <div class="type-row">${entry.types.map(createTypePill).join("")}</div>
        <p class="detail__summary">${entry.summary}</p>

        <div class="detail__grid">
          <article class="detail__block">
            <h3>Where In RBY</h3>
            <p>${entry.location}</p>
          </article>
          <article class="detail__block">
            <h3>World Interaction</h3>
            <p>${entry.role}</p>
          </article>
          <article class="detail__block">
            <h3>Evolution Path</h3>
            <p>${entry.evolution}</p>
          </article>
          <article class="detail__block">
            <h3>Version Signal</h3>
            <p>${entry.versions.join(", ")}</p>
          </article>
        </div>

        <article class="detail__section">
          <h3>Pokedex Broadcast</h3>
          ${
            flavorEntries.length
              ? `<div class="dex-entry-grid">
                  ${flavorEntries
                    .map(
                      (flavor) => `
                        <div class="dex-entry">
                          <div class="dex-entry__version">${formatVersionLabel(flavor.version)}</div>
                          <p>${flavor.text}</p>
                        </div>
                      `
                    )
                    .join("")}
                </div>`
              : `<p class="detail__fallback">Run the local PokeAPI cache script to load cartridge Pokédex text.</p>`
          }
        </article>

        <article class="detail__section">
          <h3>Known Locations</h3>
          ${renderEncounterLocations(reference)}
        </article>

        <article class="detail__section">
          <h3>Level-Up Move Chart</h3>
          ${renderMoveTable(reference)}
        </article>
      </div>

      <aside class="detail__spotlight">
        <img class="detail__art" src="${artworkPath(entry.id)}" alt="${entry.name} official artwork" onerror="this.onerror=null;this.src='${fallbackArtworkPath(entry.id)}'" />
        <div class="detail__dex-id">${String(entry.id).padStart(3, "0")}</div>
        <div class="detail__art-name">${entry.name} // Kanto behavior profile</div>
        <p class="detail__caption">${entry.fieldNote}</p>
      </aside>
    </div>
  `;
}

function render() {
  const filteredEntries = pokemon151.filter(matchesFilters);
  renderList(filteredEntries);
}

function populateFilters() {
  uniqueValues("types").forEach((type) => {
    typeFilter.insertAdjacentHTML("beforeend", `<option value="${type}">${type}</option>`);
  });

  uniqueValues("habitat").forEach((habitat) => {
    habitatFilter.insertAdjacentHTML("beforeend", `<option value="${habitat}">${habitat}</option>`);
  });
}

populateFilters();
render();

[searchInput, typeFilter, versionFilter, habitatFilter].forEach((element) => {
  element.addEventListener("input", render);
  element.addEventListener("change", render);
});

pokemonList.addEventListener("click", (event) => {
  const button = event.target.closest(".pokemon-card");
  if (!button) {
    return;
  }

  activePokemonId = Number(button.dataset.id);
  render();
});
