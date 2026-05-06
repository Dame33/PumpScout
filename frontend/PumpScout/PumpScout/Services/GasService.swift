//
//  GasService.swift
//  PumpScout
//
//  Created by Damon Lam on 2026-04-20.
//

import Foundation

enum GasError: Error {
    case badURL, networkError, decodingError
}

@MainActor
class GasService: ObservableObject {
    private let base = "192.168.2.61:8000"

    @Published var summary: GasSummary?
    @Published var isLoading = false
    @Published var errorMessage: String?

    func loadData() async {
        isLoading = true
        errorMessage = nil

        defer {
            isLoading = false
        }

        do {
            guard let refreshURL = URL(string: "http://\(base)/api/refresh") else {
                throw GasError.badURL
            }

            var req = URLRequest(url: refreshURL)
            req.httpMethod = "POST"
            _ = try await URLSession.shared.data(for: req)

            guard let summaryURL = URL(string: "http://\(base)/summary") else {
                throw GasError.badURL
            }

            let (data, _) = try await URLSession.shared.data(from: summaryURL)
            summary = try JSONDecoder().decode(GasSummary.self, from: data)

        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
