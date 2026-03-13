class CarbonService:
    def calculate_carbon_credits(self, area_hectares: float, tree_cover_ratio: float, ndvi: float):
        """
        Estimates Carbon Credits based on area, tree cover, and NDVI.
        Formula:
        Biomass = Area * Tree_Cover * Factor(NDVI)
        Carbon_Stock = Biomass * 0.5 (Carbon Fraction)
        CO2_Seq = Carbon_Stock * 3.67 (C -> CO2)
        """
        
        # 1. Estimate Biomass Density (tons/ha) based on NDVI proxy
        # This is a simplified IPCC Tier 1 approach
        if ndvi < 0.2:
            biomass_density = 0 # Non-vegetated
        elif ndvi < 0.5:
             biomass_density = 50 * ndvi # Shrub/Grass
        else:
             biomass_density = 150 * ndvi # Forest

        # 2. Total Biomass
        effective_area = area_hectares * tree_cover_ratio
        total_biomass = effective_area * biomass_density
        
        # 3. Carbon Stock (tons C)
        # Default carbon fraction of biomass is 0.47 (IPCC 2006) - rounded to 0.5
        carbon_stock = total_biomass * 0.5
        
        # 4. CO2 Equivalent (tons CO2)
        # Atomic mass ratio: 44/12 ≈ 3.67
        co2_equivalent = carbon_stock * 3.67
        
        # 5. Carbon Credits (1 Credit = 1 Ton CO2)
        carbon_credits = co2_equivalent
        
        # Confidence Score (Mocked heuristic)
        confidence_score = 0.85 if ndvi > 0.6 else 0.65
        
        return {
            "biomass_tons": round(total_biomass, 2),
            "carbon_stock_tons": round(carbon_stock, 2),
            "co2_tons": round(co2_equivalent, 2),
            "carbon_credits": round(carbon_credits, 2),
            "confidence_score": confidence_score
        }

carbon_service = CarbonService()
