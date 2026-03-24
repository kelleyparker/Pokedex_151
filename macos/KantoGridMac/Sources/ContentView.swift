import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(spacing: 0) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("National Pokedex Grid")
                        .font(.system(size: 24, weight: .bold, design: .rounded))
                    Text("Cross-generation cyber Pokédex")
                        .font(.system(size: 13, weight: .medium, design: .rounded))
                        .foregroundStyle(.secondary)
                }
                Spacer()
            }
            .padding(.horizontal, 20)
            .padding(.top, 18)
            .padding(.bottom, 14)

            Divider()

            LocalWebContainer()
        }
        .background(Color(nsColor: .windowBackgroundColor))
    }
}
