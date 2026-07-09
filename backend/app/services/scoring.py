def calculate_vk_score(parcel):

    score = 0

    # Large lot
    if parcel.lot_size and parcel.lot_size >= 1:
        score += 20
    elif parcel.lot_size and parcel.lot_size >= 0.5:
        score += 10

    # Residential zoning
    if parcel.zoning and parcel.zoning.startswith("R"):
        score += 20

    # Absentee owner
    if (
        parcel.owner_address
        and parcel.address
        and parcel.owner_address.upper() not in parcel.address.upper()
    ):
        score += 20

    # Long hold ownership
    if parcel.years_owned and parcel.years_owned >= 25:
        score += 20
    elif parcel.years_owned and parcel.years_owned >= 10:
        score += 10

    # Parcels adjacent to developer-owned land are easier to aggregate.
    if parcel.adjacent_developer_owned:
        score += 15

    if parcel.tax_delinquent:
        score += 10

    # Parcels already held by a developer are weaker acquisition targets.
    if parcel.developer_owned:
        score -= 20

    # Owner information exists
    if parcel.owner_name:
        score += 5

    return max(0, min(score, 100))
