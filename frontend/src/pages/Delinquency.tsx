import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'

import { fetchOpportunities } from '../api'
import type { OpportunityResponse } from '../api'

function csvEscape(value: string): string {
  if (value.includes(',') || value.includes('"') || value.includes('\n')) {
    return `"${value.replace(/"/g, '""')}"`
  }
  return value
}

function asCurrency(value: number | null | undefined): string {
  if (value === null || value === undefined) {
    return '-'
  }
  return `$${value.toLocaleString()}`
}

function Delinquency() {
  const [minTaxLienAmount, setMinTaxLienAmount] = useState('1000')
  const [neighborhood, setNeighborhood] = useState('')
  const [yearsOwnedMin, setYearsOwnedMin] = useState('')
  const [absenteeOnly, setAbsenteeOnly] = useState(true)
  const [limit, setLimit] = useState('250')

  const [results, setResults] = useState<OpportunityResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const totalLien = useMemo(
    () => results.reduce((sum, item) => sum + (item.tax_lien_amount ?? 0), 0),
    [results],
  )

  const delinquentCount = useMemo(
    () => results.filter((item) => item.tax_delinquent).length,
    [results],
  )

  async function loadDelinquencyList() {
    setLoading(true)
    setError(null)

    const params = new URLSearchParams({
      tax_delinquent_only: 'true',
      sort_by: 'tax_lien_amount',
      limit: limit.trim() || '250',
    })

    if (minTaxLienAmount.trim()) {
      params.set('min_tax_lien_amount', minTaxLienAmount.trim())
    }

    if (neighborhood.trim()) {
      params.set('neighborhood', neighborhood.trim())
    }

    if (yearsOwnedMin.trim()) {
      params.set('years_owned_min', yearsOwnedMin.trim())
    }

    if (absenteeOnly) {
      params.set('absentee_only', 'true')
    }

    try {
      const data = await fetchOpportunities(params)
      setResults(data)
    } catch (err) {
      setError((err as Error).message)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadDelinquencyList()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function exportCurrentResultsCsv() {
    const header = [
      'parcel_number',
      'owner',
      'owner_address',
      'owner_city_state',
      'owner_zip_code',
      'property_address',
      'neighborhood',
      'zoning',
      'tax_delinquent',
      'tax_lien_amount',
      'absentee_owner',
      'years_owned',
      'seller_probability',
      'vk_score',
      'suggested_offer',
    ]

    const rows = results.map((item) => [
      item.parcel_number,
      item.owner ?? '',
      item.owner_address ?? '',
      item.owner_city_state ?? '',
      item.owner_zip_code ?? '',
      item.address ?? '',
      item.neighborhood ?? '',
      item.zoning ?? '',
      item.tax_delinquent ? 'true' : 'false',
      item.tax_lien_amount?.toString() ?? '',
      item.absentee_owner ? 'true' : 'false',
      item.years_owned?.toString() ?? '',
      item.seller_probability?.toString() ?? '',
      item.vk_score.toString(),
      item.suggested_offer?.toString() ?? '',
    ])

    const csv = [header, ...rows]
      .map((line) => line.map((value) => csvEscape(value)).join(','))
      .join('\n')

    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.href = url
    link.download = `delinquency-outreach-${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <main>
      <h1>Delinquency Outreach</h1>
      <p>Focused view of tax-delinquent parcels ranked by lien amount, with owner contact fields ready for outreach.</p>

      <section>
        <h2>Filters</h2>

        <form
          onSubmit={(event) => {
            event.preventDefault()
            void loadDelinquencyList()
          }}
        >
          <label>
            Minimum Tax Lien Amount ($)
            <input
              type="number"
              value={minTaxLienAmount}
              onChange={(event) => setMinTaxLienAmount(event.target.value)}
            />
          </label>

          <label>
            Neighborhood
            <input value={neighborhood} onChange={(event) => setNeighborhood(event.target.value)} />
          </label>

          <label>
            Minimum Years Owned
            <input
              type="number"
              value={yearsOwnedMin}
              onChange={(event) => setYearsOwnedMin(event.target.value)}
            />
          </label>

          <label>
            Result Limit
            <input type="number" value={limit} onChange={(event) => setLimit(event.target.value)} />
          </label>

          <label>
            <span>
              <input
                type="checkbox"
                checked={absenteeOnly}
                onChange={(event) => setAbsenteeOnly(event.target.checked)}
              />
              Absentee Owners Only
            </span>
          </label>

          <div className="form-actions">
            <button type="submit" disabled={loading}>
              {loading ? 'Refreshing…' : 'Refresh List'}
            </button>
            <button type="button" disabled={loading || results.length === 0} onClick={exportCurrentResultsCsv}>
              Export CSV
            </button>
          </div>
        </form>
      </section>

      {error ? <p role="alert">{error}</p> : null}

      <section>
        <h2>Summary</h2>
        <p>Rows: {results.length}</p>
        <p>Delinquent rows: {delinquentCount}</p>
        <p>Total lien exposure: {asCurrency(totalLien)}</p>
      </section>

      {results.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Parcel</th>
              <th>Owner</th>
              <th>Owner Address</th>
              <th>Neighborhood</th>
              <th>Lien</th>
              <th>Absentee</th>
              <th>Years Owned</th>
              <th>Seller Prob.</th>
              <th>VK Score</th>
            </tr>
          </thead>
          <tbody>
            {results.map((item) => (
              <tr key={item.parcel_number}>
                <td>
                  <Link className="link-button" to={`/parcels/${item.parcel_number}`}>
                    {item.parcel_number}
                  </Link>
                </td>
                <td>{item.owner || '-'}</td>
                <td>
                  {[item.owner_address, item.owner_city_state, item.owner_zip_code]
                    .filter(Boolean)
                    .join(', ') || '-'}
                </td>
                <td>{item.neighborhood || '-'}</td>
                <td>{asCurrency(item.tax_lien_amount)}</td>
                <td>{item.absentee_owner ? 'Yes' : 'No'}</td>
                <td>{item.years_owned ?? '-'}</td>
                <td>{item.seller_probability ?? '-'}</td>
                <td>{item.vk_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No delinquency results for current filters.</p>
      )}
    </main>
  )
}

export default Delinquency