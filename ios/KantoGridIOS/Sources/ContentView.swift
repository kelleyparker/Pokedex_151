import SwiftUI

struct ContentView: View {
    var body: some View {
        NavigationStack {
            LocalWebContainer()
                .ignoresSafeArea()
                .navigationTitle("National Pokedex")
                .navigationBarTitleDisplayMode(.inline)
        }
        .tint(.cyan)
    }
}
