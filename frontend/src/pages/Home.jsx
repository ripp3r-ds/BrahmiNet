import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

export default function Home() {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [hasSearched, setHasSearched] = useState(false);

    // Quick fallback test data if backend not running
    const mockData = [
        { id: 1, text_caption: "Testing", film_series: "Dookudu", emotion: "Laughing", r2_url: "https://via.placeholder.com/400x300.png?text=Brahmi+Laughing" },
        { id: 2, text_caption: "Em chepparu sir", film_series: "Race Gurram", emotion: "Sarcastic", r2_url: "https://via.placeholder.com/400x300.png?text=Brahmi+Sarcasm" },
    ];

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setIsLoading(true);
        setHasSearched(true);

        try {
            const response = await fetch(`http://localhost:8000/search?query=${encodeURIComponent(query)}`);
            if (response.ok) {
                const data = await response.json();
                setResults(data);
            } else {
                // Fallback or handle error
                console.error("Failed to fetch");
                setResults([]);
            }
        } catch (err) {
            console.error("API not available, using empty state", err);
            // setResults(mockData); // Uncomment to test UI without backend
            setResults([]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="search-container">
            <h1 className="gradient-text">Find the Perfect Meme</h1>

            <form className="search-box" onSubmit={handleSearch}>
                <Search className="search-icon" size={24} />
                <input
                    type="text"
                    placeholder="Search for an emotion, situation, or dialogue..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
            </form>

            {isLoading && (
                <div style={{ marginTop: '3rem' }}>
                    <span className="loader"></span>
                </div>
            )}

            {hasSearched && !isLoading && results.length === 0 && (
                <div style={{ marginTop: '2rem', opacity: 0.7 }}>
                    <p>No memes found matching your brilliant query. Try rephrasing!</p>
                </div>
            )}

            {!isLoading && results.length > 0 && (
                <div className="results-grid" style={{ width: '100%' }}>
                    {results.map(meme => (
                        <div key={meme.id} className="meme-card">
                            <div className="meme-image-wrapper">
                                <img src={meme.r2_url} alt={meme.emotion || 'Meme'} loading="lazy" />
                            </div>
                            <div className="meme-info">
                                <div className="meme-tags">
                                    {meme.emotion && <span className="tag">{meme.emotion}</span>}
                                    {meme.film_series && <span className="tag">{meme.film_series}</span>}
                                </div>
                                {meme.text_caption && <h3>"{meme.text_caption}"</h3>}
                                {meme.situation && <p>{meme.situation}</p>}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
