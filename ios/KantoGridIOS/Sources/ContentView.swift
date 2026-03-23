import SwiftUI

struct ContentView: View {
    @StateObject private var store = PokedexStore()
    @State private var selectedType = "All"

    private var filteredPokemon: [Pokemon] {
        store.filteredPokemon(type: selectedType)
    }

    var body: some View {
        NavigationStack {
            ZStack {
                LinearGradient(
                    colors: [Color(red: 0.03, green: 0.08, blue: 0.13), Color.black],
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()

                if store.isLoaded {
                    ScrollView {
                        VStack(alignment: .leading, spacing: 22) {
                            heroSection
                            typeStrip
                            pokemonList
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal, 16)
                        .padding(.bottom, 32)
                    }
                    .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
                } else {
                    ProgressView("Loading Kanto Grid")
                        .tint(.cyan)
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
            .searchable(text: $store.searchText, placement: .navigationBarDrawer(displayMode: .always), prompt: "Search name, route, move, type...")
            .navigationTitle("Kanto Grid 151")
            .navigationBarTitleDisplayMode(.large)
        }
        .tint(.cyan)
    }

    private var heroSection: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("GAME BOY ERA FIELD INDEX")
                .font(.caption.weight(.bold))
                .foregroundStyle(.cyan)
                .tracking(1.6)
            Text("Native iPhone Pokédex")
                .font(.system(size: 34, weight: .black, design: .rounded))
                .foregroundStyle(.white)
            Text("Touch-first Pokédex flow for the original 151, with Red/Blue/Yellow text, locations, local artwork, and Gen 1 move charts.")
                .font(.subheadline)
                .foregroundStyle(.white.opacity(0.72))

            HStack(spacing: 12) {
                StatBadge(title: "Loaded", value: "\(store.pokemon.count)")
                StatBadge(title: "Region", value: "Kanto")
                StatBadge(title: "Cache", value: "Offline")
            }
        }
        .padding(18)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .fill(
                    LinearGradient(
                        colors: [Color(red: 0.07, green: 0.16, blue: 0.23), Color(red: 0.03, green: 0.08, blue: 0.12)],
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 28, style: .continuous)
                        .stroke(.cyan.opacity(0.24), lineWidth: 1)
                )
        )
    }

    private var typeStrip: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                ForEach(store.availableTypes, id: \.self) { type in
                    Button {
                        selectedType = type
                    } label: {
                        Text(type)
                            .font(.footnote.weight(.bold))
                            .padding(.horizontal, 14)
                            .padding(.vertical, 10)
                            .background(selectedType == type ? Color.cyan.opacity(0.24) : Color.white.opacity(0.06))
                            .foregroundStyle(selectedType == type ? .cyan : .white.opacity(0.86))
                            .clipShape(Capsule())
                            .overlay(
                                Capsule()
                                    .stroke(selectedType == type ? .cyan : .white.opacity(0.08), lineWidth: 1)
                            )
                    }
                }
            }
        }
    }

    private var pokemonList: some View {
        LazyVStack(spacing: 14) {
            ForEach(filteredPokemon) { pokemon in
                NavigationLink {
                    PokemonDetailView(pokemon: pokemon)
                } label: {
                    PokemonCard(pokemon: pokemon)
                }
                .buttonStyle(.plain)
            }
        }
    }
}

struct PokemonDetailView: View {
    let pokemon: Pokemon
    @State private var selectedSection: DetailSection = .overview

    var body: some View {
        ZStack {
            LinearGradient(
                colors: [Color(red: 0.03, green: 0.08, blue: 0.13), Color.black],
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()

            ScrollView {
                VStack(alignment: .leading, spacing: 22) {
                    detailHero
                    sectionTabs
                    activeSectionView
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(16)
                .padding(.bottom, 32)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
        }
        .navigationTitle(pokemon.name)
        .navigationBarTitleDisplayMode(.inline)
    }

    private var detailHero: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack(alignment: .top) {
                VStack(alignment: .leading, spacing: 10) {
                    Text(pokemon.dexNumber)
                        .font(.caption.weight(.bold))
                        .foregroundStyle(.cyan)
                    Text(pokemon.name)
                        .font(.system(size: 34, weight: .black, design: .rounded))
                        .foregroundStyle(.white)
                    Text(pokemon.summary)
                        .font(.subheadline)
                        .foregroundStyle(.white.opacity(0.74))
                }

                Spacer(minLength: 16)
                PokemonArtworkView(id: pokemon.id)
                    .frame(width: 132, height: 132)
            }

            HStack(spacing: 8) {
                ForEach(pokemon.types, id: \.self) { type in
                    Text(type)
                        .font(.caption.weight(.bold))
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .background(typeColor(type).opacity(0.18))
                        .foregroundStyle(typeColor(type))
                        .clipShape(Capsule())
                }
            }
        }
        .padding(18)
        .background(
            RoundedRectangle(cornerRadius: 26, style: .continuous)
                .fill(Color.white.opacity(0.05))
                .overlay(
                    RoundedRectangle(cornerRadius: 26, style: .continuous)
                        .stroke(.cyan.opacity(0.20), lineWidth: 1)
                )
        )
    }

    private var sectionTabs: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                ForEach(DetailSection.allCases) { section in
                    Button {
                        selectedSection = section
                    } label: {
                        Text(section.rawValue)
                            .font(.footnote.weight(.bold))
                            .padding(.horizontal, 14)
                            .padding(.vertical, 10)
                            .background(selectedSection == section ? Color.cyan.opacity(0.24) : Color.white.opacity(0.06))
                            .foregroundStyle(selectedSection == section ? .cyan : .white.opacity(0.88))
                            .clipShape(Capsule())
                            .overlay(
                                Capsule()
                                    .stroke(selectedSection == section ? .cyan : .white.opacity(0.10), lineWidth: 1)
                            )
                    }
                    .buttonStyle(.plain)
                }
            }
        }
    }

    @ViewBuilder
    private var activeSectionView: some View {
        switch selectedSection {
        case .overview:
            overviewSection
        case .dexText:
            dexTextSection
        case .locations:
            locationsSection
        case .moves:
            movesSection
        }
    }

    private var overviewSection: some View {
        VStack(spacing: 14) {
            InfoCard(title: "Where in RBY", text: pokemon.location)
            InfoCard(title: "World Interaction", text: pokemon.role)
            InfoCard(title: "Evolution Path", text: pokemon.evolution)
            InfoCard(title: "Field Note", text: pokemon.fieldNote)
        }
    }

    private var dexTextSection: some View {
        VStack(spacing: 14) {
            if pokemon.reference.pokedexText.isEmpty {
                InfoCard(title: "Dex Text", text: "No cartridge flavor text was loaded for this Pokémon.")
            } else {
                ForEach(["red", "blue", "yellow"], id: \.self) { version in
                    if let text = pokemon.reference.pokedexText[version] {
                        InfoCard(title: version.capitalized, text: text)
                    }
                }
            }
        }
    }

    private var locationsSection: some View {
        VStack(spacing: 14) {
            if pokemon.reference.encounterLocations.isEmpty {
                InfoCard(title: "Known Locations", text: pokemon.reference.locationFallback)
            } else {
                ForEach(pokemon.reference.encounterLocations) { group in
                    InfoCard(title: group.versionLabel, text: group.locations.joined(separator: ", "))
                }
            }
        }
    }

    private var movesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            ForEach(pokemon.reference.learnset) { move in
                HStack(spacing: 12) {
                    Text(move.move)
                        .font(.body.weight(.semibold))
                        .foregroundStyle(.white)
                    Spacer()
                    moveLevelBadge(title: "RB", value: move.redBlueLevel)
                    moveLevelBadge(title: "Y", value: move.yellowLevel)
                }
                .padding(14)
                .background(Color.white.opacity(0.05))
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))
            }
        }
    }

    private func moveLevelBadge(title: String, value: String) -> some View {
        VStack(spacing: 4) {
            Text(title)
                .font(.caption2.weight(.bold))
                .foregroundStyle(.cyan)
            Text(value)
                .font(.caption.weight(.bold))
                .foregroundStyle(.white)
        }
        .frame(width: 42, height: 42)
        .background(Color.black.opacity(0.28))
        .clipShape(RoundedRectangle(cornerRadius: 12, style: .continuous))
    }
}

struct PokemonCard: View {
    let pokemon: Pokemon

    var body: some View {
        HStack(spacing: 14) {
            PokemonArtworkView(id: pokemon.id)
                .frame(width: 78, height: 78)
                .background(Color.white.opacity(0.04))
                .clipShape(RoundedRectangle(cornerRadius: 18, style: .continuous))

            VStack(alignment: .leading, spacing: 8) {
                Text(pokemon.dexNumber)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(.cyan)
                Text(pokemon.name)
                    .font(.title3.weight(.heavy))
                    .foregroundStyle(.white)
                HStack(spacing: 8) {
                    ForEach(pokemon.types, id: \.self) { type in
                        Text(type)
                            .font(.caption.weight(.bold))
                            .padding(.horizontal, 10)
                            .padding(.vertical, 6)
                            .background(typeColor(type).opacity(0.16))
                            .foregroundStyle(typeColor(type))
                            .clipShape(Capsule())
                    }
                }
                Text(pokemon.primaryLocationLine)
                    .font(.footnote)
                    .foregroundStyle(.white.opacity(0.7))
                    .lineLimit(2)
            }

            Spacer(minLength: 0)
        }
        .padding(14)
        .background(Color.white.opacity(0.05))
        .clipShape(RoundedRectangle(cornerRadius: 22, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(.cyan.opacity(0.12), lineWidth: 1)
        )
    }
}

struct InfoCard: View {
    let title: String
    let text: String

    var bodyView: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title.uppercased())
                .font(.caption.weight(.bold))
                .foregroundStyle(.cyan)
                .tracking(1.2)
            Text(text)
                .font(.body)
                .foregroundStyle(.white.opacity(0.84))
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(16)
        .background(Color.white.opacity(0.05))
        .clipShape(RoundedRectangle(cornerRadius: 20, style: .continuous))
    }

    var body: some View {
        bodyView
    }
}

struct StatBadge: View {
    let title: String
    let value: String

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title.uppercased())
                .font(.caption2.weight(.bold))
                .foregroundStyle(.cyan.opacity(0.8))
            Text(value)
                .font(.subheadline.weight(.bold))
                .foregroundStyle(.white)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 10)
        .background(Color.white.opacity(0.05))
        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
    }
}

struct PokemonArtworkView: View {
    let id: Int

    var body: some View {
        if let image = UIImage(named: String(format: "Web/assets/official-artwork/%03d.png", id)) {
            Image(uiImage: image)
                .resizable()
                .scaledToFit()
        } else if let url = Bundle.main.url(forResource: String(format: "%03d", id), withExtension: "png", subdirectory: "Web/assets/official-artwork"),
                  let image = UIImage(contentsOfFile: url.path) {
            Image(uiImage: image)
                .resizable()
                .scaledToFit()
        } else {
            RoundedRectangle(cornerRadius: 16, style: .continuous)
                .fill(Color.white.opacity(0.04))
                .overlay(
                    Text(String(format: "#%03d", id))
                        .font(.caption.weight(.bold))
                        .foregroundStyle(.cyan)
                )
        }
    }
}

enum DetailSection: String, CaseIterable, Identifiable {
    case overview = "Overview"
    case dexText = "Dex Text"
    case locations = "Locations"
    case moves = "Moves"

    var id: String { rawValue }
}

final class PokedexStore: ObservableObject {
    @Published var pokemon: [Pokemon] = []
    @Published var searchText = ""

    var isLoaded: Bool { !pokemon.isEmpty }

    var availableTypes: [String] {
        ["All"] + Array(Set(pokemon.flatMap(\.types))).sorted()
    }

    init() {
        load()
    }

    func filteredPokemon(type: String) -> [Pokemon] {
        pokemon.filter { pokemon in
            let matchesType = type == "All" || pokemon.types.contains(type)
            let matchesSearch =
                searchText.isEmpty ||
                pokemon.searchBlob.localizedCaseInsensitiveContains(searchText)
            return matchesType && matchesSearch
        }
    }

    private func load() {
        guard let url = Bundle.main.url(forResource: "native-kanto-pokedex", withExtension: "json", subdirectory: "Web"),
              let data = try? Data(contentsOf: url),
              let decoded = try? JSONDecoder().decode([Pokemon].self, from: data)
        else {
            return
        }

        pokemon = decoded.sorted { $0.id < $1.id }
    }
}

struct Pokemon: Identifiable, Decodable {
    let id: Int
    let name: String
    let types: [String]
    let habitat: String
    let location: String
    let availability: String
    let summary: String
    let role: String
    let evolution: String
    let versions: [String]
    let fieldNote: String
    let reference: PokemonReference

    var dexNumber: String {
        String(format: "#%03d", id)
    }

    var primaryLocationLine: String {
        if let first = reference.encounterLocations.first {
            return "\(first.versionLabel): \(first.locations.joined(separator: ", "))"
        }
        return location
    }

    var searchBlob: String {
        [
            name,
            types.joined(separator: " "),
            habitat,
            location,
            summary,
            role,
            evolution,
            fieldNote,
            reference.encounterLocations.flatMap(\.locations).joined(separator: " "),
            reference.learnset.map(\.move).joined(separator: " "),
            reference.pokedexText.values.joined(separator: " ")
        ].joined(separator: " ")
    }
}

struct PokemonReference: Decodable {
    let encounterLocations: [EncounterGroup]
    let learnset: [MoveEntry]
    let locationFallback: String
    let pokedexText: [String: String]
}

struct EncounterGroup: Decodable, Identifiable {
    let versionLabel: String
    let locations: [String]

    var id: String { versionLabel }
}

struct MoveEntry: Decodable, Identifiable {
    let move: String
    let redBlueLevel: String
    let yellowLevel: String

    var id: String { move }
}

func typeColor(_ type: String) -> Color {
    switch type {
    case "Grass": return Color.green
    case "Poison": return Color.purple
    case "Fire": return Color.orange
    case "Water": return Color.blue
    case "Electric": return Color.yellow
    case "Bug": return Color(red: 0.67, green: 0.85, blue: 0.26)
    case "Ground": return Color(red: 0.86, green: 0.67, blue: 0.33)
    case "Rock": return Color(red: 0.76, green: 0.67, blue: 0.48)
    case "Psychic": return Color.pink
    case "Ice": return Color.cyan
    case "Ghost": return Color.indigo
    case "Dragon": return Color(red: 0.45, green: 0.57, blue: 1.0)
    case "Fighting": return Color.red
    case "Flying": return Color(red: 0.67, green: 0.79, blue: 1.0)
    default: return Color.white
    }
}
