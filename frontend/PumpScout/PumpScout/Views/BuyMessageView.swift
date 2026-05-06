//
//  BuyMessageView.swift
//  PumpScout
//
//  Created by Damon Lam on 2026-04-21.
//

import SwiftUI

struct BuyMessageView: View {
    let message: String
    let background: String
    
    private var color: Color{
        switch background {
        case "green": return .green
        case "red": return .red
        default: return .orange
        }
    }
    
    var body: some View {
        Text(message)
            .font(.caption)
            .fontWeight(.medium)
            .padding(.horizontal, 10)
            .padding(.vertical, 5)
            .background(color.opacity(0.15))
            .foregroundStyle(color)
            .clipShape(Capsule())
    }
}


