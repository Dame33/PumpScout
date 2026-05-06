//
//  GasModels.swift
//  PumpScout
//
//  Created by Damon Lam on 2026-04-20.
//

import Foundation

struct GasSummary: Codable {
    let currentPrice: Double
    let tomorrowPredictedPrice: Double
    let updatedAt: String
    let sevenDayHistory: [DailyGas]
    let buyMessage: String
    let background: String
    let source: String
    
}

struct DailyGas: Codable {
    let dateLabel: String
    let price: Double
}
