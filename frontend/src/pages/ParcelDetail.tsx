import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchParcel } from '../api'
import type { ParcelResponse } from '../api'

function ParcelDetail() {
  const { parcelNumber } = useParams<{ parcelNumber: string }>()
  const [parcel, setParcel] = useState<ParcelResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!parcelNumber) return
    setLoading(true)
    setError(null)

    fetchParcel(parcelNumber)
      .then(setParcel)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [parcelNumber])

  if (loading) {
    return (
      <main>
        <h1>Parcel Detail</h1>
        <p>Loading...</p>
      </main>
    )
  }

  if (error) {
    return (
      <main>
        <h1>Parcel Detail</h1>
        <p role="alert">{error}</p>
        <p>
          <Link className="link-button" to="/search">
            Back to search
          </Link>
        </p>
      </main>
    )
  }

  if (!parcel) {
    return (
      <main>
        <h1>Parcel Detail</h1>
        <p>Parcel not found.</p>
        <p>
          <Link className="link-button" to="/search">
            Back to search
          </Link>
        </p>
      </main>
    )
  }

  return (
    <main>
      <h1>Parcel Detail</h1>
      <p>
        <Link className="link-button" to="/search">
          Back to search
        </Link>
      </p>

      <dl>
        <dt>Parcel Number</dt>
        <dd>{parcel.parcel_number}</dd>

        <dt>GPIN</dt>
        <dd>{parcel.gpin || '-'}</dd>

        <dt>Address</dt>
        <dd>{parcel.address || '-'}</dd>

        <dt>City / State</dt>
        <dd>{[parcel.city, parcel.state].filter(Boolean).join(', ') || '-'}</dd>

        <dt>Zoning</dt>
        <dd>{parcel.zoning || '-'}</dd>

        <dt>Property Type</dt>
        <dd>{parcel.property_type || '-'}</dd>

        <dt>Neighborhood</dt>
        <dd>{parcel.neighborhood || '-'}</dd>

        <dt>Acres</dt>
        <dd>{parcel.lot_size ?? '-'}</dd>

        <dt>Years Owned</dt>
        <dd>{parcel.years_owned ?? '-'}</dd>

        <dt>Estimated Unit Capacity</dt>
        <dd>{parcel.estimated_units ?? '-'}</dd>

        <dt>Seller Probability</dt>
        <dd>{parcel.seller_probability ?? '-'}</dd>

        <dt>Suggested Offer Range</dt>
        <dd>
          {parcel.offer_low && parcel.offer_high
            ? `$${parcel.offer_low.toLocaleString()} - $${parcel.offer_high.toLocaleString()}`
            : '-'}
        </dd>

        <dt>Suggested Offer Midpoint</dt>
        <dd>{parcel.suggested_offer ? `$${parcel.suggested_offer.toLocaleString()}` : '-'}</dd>

        <dt>Tax Delinquent</dt>
        <dd>{parcel.tax_delinquent ? 'Yes' : 'No'}</dd>

        <dt>Tax Lien Amount</dt>
        <dd>{parcel.tax_lien_amount ? `$${parcel.tax_lien_amount.toLocaleString()}` : '-'}</dd>

        <dt>Inside SIA</dt>
        <dd>{parcel.sia_flag ? 'Yes' : 'No'}</dd>

        <dt>Adjacent To Developer-Owned Parcel</dt>
        <dd>{parcel.adjacent_developer_owned ? 'Yes' : 'No'}</dd>

        <dt>Owner</dt>
        <dd>{parcel.owner_name || '-'}</dd>

        <dt>Owner Address</dt>
        <dd>{parcel.owner_address || '-'}</dd>

        <dt>Owner City/State</dt>
        <dd>{parcel.owner_city_state || '-'}</dd>

        <dt>Owner Zip</dt>
        <dd>{parcel.owner_zip_code || '-'}</dd>
      </dl>

      {parcel.latest_assessment ? (
        <section>
          <h2>Latest Assessment</h2>
          <dl>
            <dt>Tax Year</dt>
            <dd>{parcel.latest_assessment.tax_year}</dd>
            <dt>Land Value</dt>
            <dd>{parcel.latest_assessment.land_value ?? '-'}</dd>
            <dt>Improvement Value</dt>
            <dd>{parcel.latest_assessment.improvement_value ?? '-'}</dd>
            <dt>Market Value</dt>
            <dd>{parcel.latest_assessment.market_value ?? '-'}</dd>
            <dt>Assessed Value</dt>
            <dd>{parcel.latest_assessment.assessed_value ?? '-'}</dd>
            <dt>Remarks</dt>
            <dd>{parcel.latest_assessment.remarks || '-'}</dd>
          </dl>
        </section>
      ) : (
        <p>No assessment data available.</p>
      )}
    </main>
  )
}

export default ParcelDetail
