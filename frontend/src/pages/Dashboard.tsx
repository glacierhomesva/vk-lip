import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { fetchOpportunities } from '../api'
import type { OpportunityResponse } from '../api'

interface DashboardSection {
  title: string
  description: string
  params: URLSearchParams
}

const sections: DashboardSection[] = [
  {
    title: 'Highest Acquisition Probability This Month',
    description: 'Long-hold residential parcels sorted by seller probability for current outreach.',
    params: new URLSearchParams({ years_owned_min: '10', sort_by: 'seller_probability', limit: '10' }),
  },
  {
    title: '4+ Unit Residential Candidates',
    description: 'Residential parcels with a heuristic estimated capacity of four or more units.',
    params: new URLSearchParams({ min_estimated_units: '4', sort_by: 'estimated_units', limit: '10' }),
  },
  {
    title: 'Adjacent To Developer-Owned Parcels',
    description: 'Parcels that already touch developer-owned land and may be easier to assemble.',
    params: new URLSearchParams({ adjacent_developer_owned_only: 'true', sort_by: 'vk_score', limit: '10' }),
  },
  {
    title: 'Offer-Range Watchlist',
    description: 'Higher-scoring parcels with a suggested heuristic offer range based on assessment, tenure, and probability.',
    params: new URLSearchParams({ years_owned_min: '10', sort_by: 'suggested_offer', limit: '10' }),
  },
]

function Dashboard() {
  const [results, setResults] = useState<Record<string, OpportunityResponse[]>>({})
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let active = true

    Promise.all(
      sections.map(async (section) => {
        const data = await fetchOpportunities(section.params)
        return [section.title, data.slice(0, 5)] as const
      }),
    )
      .then((entries) => {
        if (!active) return
        setResults(Object.fromEntries(entries))
      })
      .catch((err) => {
        if (!active) return
        setError((err as Error).message)
      })

    return () => {
      active = false
    }
  }, [])

  return (
    <main>
      <h1>Dashboard</h1>
      <p>VK-LIP now pushes a few curated opportunity lists instead of waiting for a manual search.</p>

      <section>
        <h2>What you can do</h2>
        <ul>
          <li>Review curated parcel lists for long-hold neighborhoods and outreach priorities.</li>
          <li>Open any parcel to review ownership details, tenure, and the latest assessment.</li>
          <li>Use search filters for exact parcel lookups and custom opportunity queries.</li>
        </ul>
      </section>

      <section>
        <h2>Current Signal Coverage</h2>
        <p>Neighborhood, years-owned, and developer-adjacency are populated from source data. SIA is reserved for a future proprietary overlay and is not active yet.</p>
        <p>VK Score is a 0 to 100 scale where higher is better.</p>
        <p>Estimated units are heuristic zoning-capacity guesses, and offer ranges are valuation heuristics. Neither should be treated as legal or appraisal advice.</p>
      </section>

      {error ? <p role="alert">{error}</p> : null}

      {sections.map((section) => (
        <section key={section.title}>
          <h2>{section.title}</h2>
          <p>{section.description}</p>

          {results[section.title]?.length ? (
            <table>
              <thead>
                <tr>
                  <th>Parcel</th>
                  <th>Neighborhood</th>
                  <th>Zoning</th>
                  <th>Acres</th>
                  <th>Years Owned</th>
                  <th>Est. Units</th>
                  <th>Seller Prob.</th>
                  <th>Suggested Offer</th>
                  <th>Score</th>
                </tr>
              </thead>
              <tbody>
                {results[section.title].map((item) => (
                  <tr key={`${section.title}-${item.parcel_number}`}>
                    <td>
                      <Link className="link-button" to={`/parcels/${item.parcel_number}`}>
                        {item.parcel_number}
                      </Link>
                    </td>
                    <td>{item.neighborhood || '-'}</td>
                    <td>{item.zoning || '-'}</td>
                    <td>{item.acres ?? '-'}</td>
                    <td>{item.years_owned ?? '-'}</td>
                    <td>{item.estimated_units ?? '-'}</td>
                    <td>{item.seller_probability ?? '-'}</td>
                    <td>{item.suggested_offer ? `$${item.suggested_offer.toLocaleString()}` : '-'}</td>
                    <td>{item.vk_score}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p>No matching parcels yet.</p>
          )}
        </section>
      ))}

      <p>
        <Link className="link-button" to="/search">
          Go to Parcel Search
        </Link>
      </p>
    </main>
  )
}

export default Dashboard
