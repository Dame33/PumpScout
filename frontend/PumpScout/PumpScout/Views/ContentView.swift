//
//  ContentView.swift
//  PumpScout
//
//  Created by Damon Lam on 2026-04-20.
//

import SwiftUI

struct ContentView: View {
    @StateObject private var service = GasService()

    var body: some View {
        NavigationStack {
            ZStack {
                Color(.systemGroupedBackground)
                    .ignoresSafeArea()

                if service.isLoading {
                    VStack(spacing: 12) {
                        ProgressView()
                        Text("Fetching prices...")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                } else if let error = service.errorMessage {
                    VStack(spacing: 16) {
                        Text("⚠️ Error")
                            .font(.title2)

                        Text(error)
                            .multilineTextAlignment(.center)
                            .padding()
                            .background(Color.red.opacity(0.1))
                            .cornerRadius(8)

                        Button("Try again") {
                            Task { await service.loadData() }
                        }
                    }
                    .padding()
                } else if let summary = service.summary {
                    ScrollView {
                        VStack(spacing: 12) {
                            PriceHeaderView(summary: summary)
                            HistoryChartView(history: summary.sevenDayHistory)

                            Button {
                                Task { await service.loadData() }
                            } label: {
                                Text("Refresh prices")
                                    .font(.headline)
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 14)
                            }
                            .buttonStyle(.bordered)
                            .tint(.primary)

                            Text("Updated \(formattedUpdate(summary.updatedAt)) · Source: \(summary.source)")
                                .font(.caption)
                                .foregroundStyle(.tertiary)
                                .padding(.top, 2)
                        }
                        .padding(.horizontal, 16)
                        .padding(.top, 10)
                        .padding(.bottom, 24)
                    }
                    .refreshable {
                        await service.loadData()
                    }
                } else {
                    Color.clear
                }
            }
            .navigationTitle("Toronto Gas")
            .navigationBarTitleDisplayMode(.inline)
            .task {
                await service.loadData()
            }
        }
    }

    private func formattedUpdate(_ raw: String) -> String {
        raw.replacingOccurrences(of: "T", with: " ")
    }
}
