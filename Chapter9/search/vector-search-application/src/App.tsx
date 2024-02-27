import React, { useEffect, useState } from 'react'
import SearchApplicationClient from '@elastic/search-application-client'
import {SearchTotalHits} from "@elastic/elasticsearch/lib/api/types";


import './App.css'

const request = SearchApplicationClient(
    'movie_vector_search_application',
    'https://xxx.cloud.es.io:443',
    'xxx',
  {
    facets: {
      director: {
        type: 'terms',
        field: 'director.keyword',
        size: 10,
        disjunctive: true,
      },
      genre: {
        type: 'terms',
        size: 10,
        field: 'genre',
      },
    },
  }
)


function Facets({ facets, addFilter, removeFilter, filters }: any) {
  if (!facets) {
    return null
  }
  return (
    <div className="md:w-1/4 bg-gray-100 p-4">
      {facets &&
        facets.map((facet: any) => {
          return (
            <div key={facet.name} className="pb-4">
              <h3 className="text-base font-semibold mb-2 uppercase">
                {facet.name}
              </h3>
              {facet.entries.map((bucket: any) => {
                const isSelected =
                  filters[facet.name] &&
                  filters[facet.name].includes(bucket.value)
                return (
                  <ul key={bucket.value}>
                    <li
                      className={`pb-0.5 cursor-pointer ${
                        isSelected ? 'font-semibold' : ''
                      }`}
                      onClick={() => {
                        if (!isSelected) {
                          addFilter(facet.name, bucket.value)
                        } else {
                          removeFilter(facet.name, bucket.value)
                        }
                      }}
                    >
                      {bucket.value} ({bucket.count})
                    </li>
                  </ul>
                )
              })}
            </div>
          )
        })}
    </div>
  )
}

function App() {
  const [query, setQuery] = useState('')
  const [page, setPage] = useState(1)
  const [results, setResults] = useState<any>(null)
  const [filters, setFilters] = useState<any>({})

  const doSearch = async () => {
    const r = request()
      .setSort(['_score'])
      .query(query)
      .setPageSize(8)
      .setFrom(12 * (page - 1))
      /*.addParameter('_es_sort_fields', ['release_year'])*/

    for (const [key, value] of Object.entries(filters)) {
      r.addFacetFilter(key, value as string)
    }

    const results = await r.search()

    setResults(results)


  }

  const handleSearch = async (e: any) => {
    e.preventDefault()
    setPage(1)
    doSearch()
  }

  const handleClickTracking = (hit: any) => (e: any) => {
    e.preventDefault()

    const url = (hit._source as {wiki_page: string}).wiki_page

    window.open(url, '_blank');
  };


  useEffect(() => {
    doSearch()

    window.scroll({ top: 0, behavior: 'smooth' })
  }, [filters, page])

  return (
    <div className="flex flex-col md:flex-row">
      <Facets
        facets={results && results.facets}
        filters={filters}
        addFilter={(filter: any, value: any) => {
          const existingFilters = filters[filter] || []
          setFilters({
            ...filters,
            [filter]: [...existingFilters, value],
          })
          setPage(1)
        }}
        removeFilter={(filter: any, value: any) => {
          const existingFilters = filters[filter] || []
          setFilters({
            ...filters,
            [filter]: existingFilters.filter((v: any) => v !== value),
          })
          setPage(1)
        }}
      />

      <div className="md:w-3/4 p-4">
        <form onSubmit={handleSearch} className="w-full mb-4 flex space-x-2">
          <input
            placeholder="search"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:border-blue-500"
            type="text"
            onChange={(e) => {
              e.preventDefault()
              setQuery(e.target.value)
            }}
          />
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded-md"
          >
            Search
          </button>
        </form>
        <div className="mt-4">
          <p className="text-gray-500">{results?.hits?.total?.value} Results</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {results &&
            results.hits.hits.map((hit: any) => {
              return (
                <div
                  key={hit._id}
                  className="bg-white rounded-lg shadow-md p-4"
                >
                  <h3 className="text-lg font-semibold"><a href={hit._source.wiki_page} onClick={handleClickTracking(hit)}>{hit._source.title}</a>
                  </h3>
                  <p>{hit._source.release_year}</p>
                  <p className="fixed-height">{hit._source.plot}</p>
                </div>
              )
            })}
        </div>
        <div className="mt-4 flex justify-center gap-4">
          {page > 1 && (
            <button
              className="bg-blue-500 text-white px-4 py-2 rounded-md"
              onClick={() => setPage(page - 1)}
            >
              Prev Page
            </button>
          )}
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded-md"
            onClick={() => setPage(page + 1)}
          >
            Next Page
          </button>
        </div>
      </div>
    </div>
  )
}

export default App
