const searchInput = document.querySelector("#search");
const typeFilter = document.querySelector("#typeFilter");
const versionFilter = document.querySelector("#versionFilter");
const habitatFilter = document.querySelector("#habitatFilter");
const generationFilter = document.querySelector("#generationFilter");
const pokemonList = document.querySelector("#pokemonList");
const pokemonDetail = document.querySelector("#pokemonDetail");
const resultsCount = document.querySelector("#resultsCount");
const dexRangeStat = document.querySelector("#dexRangeStat");
const generationStat = document.querySelector("#generationStat");
const gameStat = document.querySelector("#gameStat");

const pokedexEntries =
  typeof window !== "undefined" && Array.isArray(window.pokedexEntries) ? window.pokedexEntries : [];
const pokedexReferenceData =
  typeof window !== "undefined" && window.pokedexReferenceData ? window.pokedexReferenceData : {};

const PAGE_SIZE = 72;
let activePokemonId = pokedexEntries[0]?.id || 1;
let visibleCount = PAGE_SIZE;

function formatDexNumber(id) {
  return `#${String(id).padStart(4, "0")}`;
}

function localArtworkPath(id) {
  if (id <= 151) {
    return `./assets/official-artwork/${String(id).padStart(3, "0")}.png`;
  }
  return fallbackArtworkPath(id);
}

function fallbackArtworkPath(id) {
  return `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${id}.png`;
}

function uniqueValues(key) {
  return [...new Set(pokedexEntries.flatMap((entry) => (Array.isArray(entry[key]) ? entry[key] : [entry[key]])))]
    .filter(Boolean)
    .sort((left, right) => left.localeCompare(right));
}

function createTypePill(type) {
  return `<span class="type-pill" data-type="${type}">${type}</span>`;
}

function getReference(entry) {
  return pokedexReferenceData[String(entry.id)] || null;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderEncounterLocations(reference) {
  if (!reference || !reference.encounterLocations || !reference.encounterLocations.length) {
    return `<p>${escapeHtml(reference?.locationFallback || "No encounter data available.")}</p>`;
  }

  return `
    <ul class="detail__list">
      ${reference.encounterLocations
        .map(
          (location) => `
            <li>
              <strong>${escapeHtml(location.versionLabel)}:</strong> ${escapeHtml(location.locations.join(", "))}
            </li>
          `
        )
        .join("")}
    </ul>
  `;
}

function matchesFilters(entry) {
  const query = searchInput.value.trim().toLowerCase();
  const type = typeFilter.value;
  const version = versionFilter.value;
  const habitat = habitatFilter.value;
  const generation = generationFilter.value;
  const reference = getReference(entry);
  const encounterBlob = reference?.encounterLocations
    ? reference.encounterLocations
        .map((group) => `${group.versionLabel} ${group.locations.join(" ")}`)
        .join(" ")
    : "";

  const matchesQuery =
    !query ||
    [
      entry.name,
      entry.types.join(" "),
      entry.habitat,
      entry.generation,
      entry.location,
      entry.summary,
      entry.evolution,
      encounterBlob,
      reference?.flavorText || "",
      reference?.genus || "",
    ]
      .join(" ")
      .toLowerCase()
      .includes(query);

  const matchesType = type === "All" || entry.types.includes(type);
  const matchesVersion = version === "All" || entry.versions.includes(version);
  const matchesHabitat = habitat === "All" || entry.habitat === habitat;
  const matchesGeneration = generation === "All" || entry.generation === generation;

  return matchesQuery && matchesType && matchesVersion && matchesHabitat && matchesGeneration;
}

function renderList(entries) {
  const visibleEntries = entries.slice(0, visibleCount);
  const label =
    entries.length > visibleEntries.length
      ? `Showing ${visibleEntries.length} of ${entries.length} entries`
      : `${entries.length} entr${entries.length === 1 ? "y" : "ies"}`;
  resultsCount.textContent = label;

  if (!entries.length) {
    pokemonList.innerHTML = `
      <div class="empty-state">
        <div>
          <h3>No Pokemon matched the current scan.</h3>
          <p>Try a broader search or clear one of the filters.</p>
        </div>
      </div>
    `;
    pokemonDetail.innerHTML = "";
    return;
  }

  if (!visibleEntries.find((entry) => entry.id === activePokemonId)) {
    activePokemonId = visibleEntries[0].id;
  }

  const cardsMarkup = visibleEntries
    .map(
      (entry) => `
        <button class="pokemon-card ${entry.id === activePokemonId ? "is-active" : ""}" data-id="${entry.id}">
          <div class="pokemon-card__top">
            <div>
              <div class="pokemon-card__number">${formatDexNumber(entry.id)}</div>
              <div class="pokemon-card__name">${escapeHtml(entry.name)}</div>
            </div>
            <img
              class="pokemon-card__art"
              src="${localArtworkPath(entry.id)}"
              alt="${escapeHtml(entry.name)} artwork"
              loading="lazy"
              onerror="this.onerror=null;this.src='${fallbackArtworkPath(entry.id)}'"
            />
            <div class="chip-row">
              ${entry.types.map(createTypePill).join("")}
            </div>
          </div>
          <div class="pokemon-card__meta">${escapeHtml(`${entry.generation} • ${entry.habitat}`)}</div>
        </button>
      `
    )
    .join("");

  const loadMoreMarkup =
    entries.length > visibleEntries.length
      ? `
        <button class="pokemon-card pokemon-card--load-more" type="button" data-action="load-more">
          <div class="pokemon-card__top">
            <div>
              <div class="pokemon-card__number">MORE</div>
              <div class="pokemon-card__name">Load next ${Math.min(PAGE_SIZE, entries.length - visibleEntries.length)} entries</div>
            </div>
          </div>
          <div class="pokemon-card__meta">${entries.length - visibleEntries.length} more remaining</div>
        </button>
      `
      : "";

  pokemonList.innerHTML = cardsMarkup + loadMoreMarkup;

  renderDetail(visibleEntries.find((entry) => entry.id === activePokemonId));
}

function renderDetail(entry) {
  if (!entry) {
    pokemonDetail.innerHTML = "";
    return;
  }

  const reference = getReference(entry);
  const versionsText = entry.versions.length ? entry.versions.join(", ") : "Special or non-wild only";

  pokemonDetail.innerHTML = `
    <div class="detail__hero">
      <div class="detail__identity">
        <div class="detail__header">
          <div class="detail__number">${formatDexNumber(entry.id)}</div>
          <div class="chip-row">
            <span class="chip">${escapeHtml(entry.generation)}</span>
            <span class="chip">${escapeHtml(entry.availability)}</span>
          </div>
        </div>
        <h2 class="detail__name">${escapeHtml(entry.name)}</h2>
        <div class="type-row">${entry.types.map(createTypePill).join("")}</div>
        <p class="detail__summary">${escapeHtml(entry.summary)}</p>

        <div class="detail__grid">
          <article class="detail__block">
            <h3>Habitat</h3>
            <p>${escapeHtml(entry.habitat)}</p>
          </article>
          <article class="detail__block">
            <h3>Encounter Snapshot</h3>
            <p>${escapeHtml(entry.location)}</p>
          </article>
          <article class="detail__block">
            <h3>Evolution Path</h3>
            <p>${escapeHtml(entry.evolution)}</p>
          </article>
          <article class="detail__block">
            <h3>Encountered Games</h3>
            <p>${escapeHtml(versionsText)}</p>
          </article>
        </div>

        <article class="detail__section">
          <h3>Species Notes</h3>
          <div class="dex-entry-grid">
            <div class="dex-entry">
              <div class="dex-entry__version">${escapeHtml(reference?.genus || "Pokemon")}</div>
              <p>${escapeHtml(reference?.flavorText || entry.summary)}</p>
            </div>
          </div>
        </article>

        <article class="detail__section">
          <h3>Known Locations By Game</h3>
          ${renderEncounterLocations(reference)}
        </article>
      </div>

      <aside class="detail__spotlight">
        <img
          class="detail__art"
          src="${localArtworkPath(entry.id)}"
          alt="${escapeHtml(entry.name)} official artwork"
          onerror="this.onerror=null;this.src='${fallbackArtworkPath(entry.id)}'"
        />
        <div class="detail__dex-id">${String(entry.id).padStart(4, "0")}</div>
        <div class="detail__art-name">${escapeHtml(`${entry.name} // National field profile`)}</div>
        <p class="detail__caption">${escapeHtml(entry.location)}</p>
      </aside>
    </div>
  `;
}

function render() {
  renderList(pokedexEntries.filter(matchesFilters));
}

function populateFilters() {
  uniqueValues("types").forEach((type) => {
    typeFilter.insertAdjacentHTML("beforeend", `<option value="${escapeHtml(type)}">${escapeHtml(type)}</option>`);
  });

  uniqueValues("versions").forEach((version) => {
    versionFilter.insertAdjacentHTML(
      "beforeend",
      `<option value="${escapeHtml(version)}">${escapeHtml(version)}</option>`
    );
  });

  uniqueValues("habitat").forEach((habitat) => {
    habitatFilter.insertAdjacentHTML(
      "beforeend",
      `<option value="${escapeHtml(habitat)}">${escapeHtml(habitat)}</option>`
    );
  });

  uniqueValues("generation").forEach((generation) => {
    generationFilter.insertAdjacentHTML(
      "beforeend",
      `<option value="${escapeHtml(generation)}">${escapeHtml(generation)}</option>`
    );
  });
}

function populateStats() {
  if (!pokedexEntries.length) {
    return;
  }

  dexRangeStat.textContent = `0001-${String(pokedexEntries[pokedexEntries.length - 1].id).padStart(4, "0")}`;
  generationStat.textContent = String(uniqueValues("generation").length);
  gameStat.textContent = String(uniqueValues("versions").length);
}

populateFilters();
populateStats();
render();

[searchInput, typeFilter, versionFilter, habitatFilter, generationFilter].forEach((element) => {
  const rerender = () => {
    visibleCount = PAGE_SIZE;
    render();
  };
  element.addEventListener("input", rerender);
  element.addEventListener("change", rerender);
});

pokemonList.addEventListener("click", (event) => {
  const loadMoreButton = event.target.closest("[data-action='load-more']");
  if (loadMoreButton) {
    visibleCount += PAGE_SIZE;
    render();
    return;
  }

  const button = event.target.closest(".pokemon-card");
  if (!button) {
    return;
  }

  activePokemonId = Number(button.dataset.id);
  render();
});
