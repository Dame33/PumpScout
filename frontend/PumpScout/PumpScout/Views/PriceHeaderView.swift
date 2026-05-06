//
//  PriceHeaderView.swift
//  PumpScout
//
//  Created by Damon Lam on 2026-04-20.
//

import SwiftUI

struct PriceHeaderView: View {
    let summary: GasSummary

    private var badgeBackground: Color {
        switch summary.background.lowercased() {
        case "green":
            return Color.green.opacity(0.18)
        case "yellow", "orange":
            return Color.orange.opacity(0.18)
        case "red":
            return Color.red.opacity(0.16)
        default:
            return Color.gray.opacity(0.14)
        }
    }

    private var badgeText: Color {
        switch summary.background.lowercased() {
        case "green":
            return .green
        case "yellow", "orange":
            return .orange
        case "red":
            return .red
        default:
            return .secondary
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("TODAY'S PRICE")
                .font(.caption)
                .foregroundStyle(.secondary)

            HStack(alignment: .firstTextBaseline, spacing: 4) {
                Text(summary.currentPriceCents, format: .number.precision(.fractionLength(1)))
                    .font(.system(size: 58, weight: .semibold, design: .default))
                    .foregroundStyle(.primary)

                Text("¢/L")
                    .font(.title2)
                    .foregroundStyle(.secondary)
            }

            HStack(alignment: .center) {
                Text("Tomorrow: \(summary.tomorrowPredictedPrice, specifier: "%.1f")¢")
                    .font(.title3)
                    .foregroundStyle(.secondary)

                Spacer()

                Text(summary.buyMessage)
                
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(badgeText)
                    .padding(.horizontal, 18)
                    .padding(.vertical, 8)
                    .background(badgeBackground)
                    .clipShape(Capsule())
            }
        }
        .padding(20)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.white))
        .clipShape(RoundedRectangle(cornerRadius: 18))
        .overlay(
            RoundedRectangle(cornerRadius: 18)
                .stroke(Color.black.opacity(0.08), lineWidth: 1)
        )
    }
}
