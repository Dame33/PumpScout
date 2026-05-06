//
//  HistoryChartView.swift
//  PumpScout
//
//  Created by Damon Lam on 2026-04-21.
//

import SwiftUI
import Charts

struct HistoryChartView: View {
    let history: [DailyGas]

    private var avg: Double {
        history.isEmpty ? 0 : history.map(\.price).reduce(0, +) / Double(history.count)
    }

    private var low: Double {
        history.map(\.price).min() ?? 0
    }

    private var high: Double {
        history.map(\.price).max() ?? 0
    }

    // Wider fixed-looking range like the mockup so bars don’t look exaggerated
    private var minPrice: Double {
        floor((low - 3) / 1) * 1
    }

    private var maxPrice: Double {
        ceil((high + 3) / 1) * 1
    }

    private func shortLabel(_ label: String) -> String {
        let cleaned = label.replacingOccurrences(of: ",", with: "")
        let parts = cleaned.split(separator: " ")
        guard parts.count >= 2 else { return label }

        let month = String(parts[0].prefix(3))
        let day = String(parts[1])
        return "\(month) \(day)"
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            Text("7-DAY HISTORY")
                .font(.caption)
                .foregroundStyle(.secondary)

            Chart(Array(history.enumerated()), id: \.element.dateLabel) { index, day in
                BarMark(
                    x: .value("Date", shortLabel(day.dateLabel)),
                    yStart: .value("Floor", minPrice),
                    yEnd: .value("Price", day.price)
                )
                .clipShape(RoundedRectangle(cornerRadius: 6))
                .foregroundStyle(
                    index == history.count - 1
                    ? Color.blue
                    : Color.blue.opacity(0.35)
                )
            }
            .chartYScale(domain: minPrice...maxPrice)
            .chartYAxis(.hidden)
            .chartXAxis {
                AxisMarks { value in
                    AxisValueLabel {
                        if let s = value.as(String.self) {
                            Text(s)
                                .font(.caption2)
                                .foregroundStyle(.secondary)
                        }
                    }
                    AxisTick(stroke: StrokeStyle(lineWidth: 0))
                    AxisGridLine(stroke: StrokeStyle(lineWidth: 0))
                }
            }
            .frame(height: 150)

            HStack(spacing: 12) {
                StatPill(label: "7-day avg", value: avg)
                StatPill(label: "7-day low", value: low)
                StatPill(label: "7-day high", value: high)
            }
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.secondarySystemBackground))
        .clipShape(RoundedRectangle(cornerRadius: 18))
        .overlay(
            RoundedRectangle(cornerRadius: 18)
                .stroke(Color.black.opacity(0.08), lineWidth: 1)
        )
    }
}

struct StatPill: View {
    let label: String
    let value: Double

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text("\(value, specifier: "%.1f")¢")
                .font(.title3.weight(.semibold))
                .foregroundStyle(.primary)

            Text(label)
                .font(.caption)
                .foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}
