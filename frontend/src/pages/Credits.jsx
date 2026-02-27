export default function Credits() {
    return (
        <div className="page-container">
            <h2 className="gradient-text">Credits & Acknowledgements</h2>

            <p>
                <strong>Concept & Architecture:</strong> Built using a modern stack combining FastAPI,
                PostgreSQL (PGVector), Cloudflare R2, and React.
            </p>

            <p>
                <strong>Meme Legends:</strong> A massive tribute to Dr. Brahmanandam Garu,
                without whom Telugu cinema and internet culture would not be the same.
            </p>

            <p>
                <strong>Built with:</strong>
            </p>
            <ul style={{ listStyleType: 'none', paddingLeft: 0, marginTop: '1rem' }}>
                <li style={{ marginBottom: '0.8rem' }}>• <strong>AI Engine:</strong> OpenAI / Gemini models orchestrated via Langchain & Instructor.</li>
                <li style={{ marginBottom: '0.8rem' }}>• <strong>Data Storage:</strong> Neon Serverless Postgres with PGVector extension.</li>
                <li style={{ marginBottom: '0.8rem' }}>• <strong>Object Storage:</strong> Cloudflare R2 for extremely fast edge delivery of images.</li>
                <li style={{ marginBottom: '0.8rem' }}>• <strong>Caching:</strong> Upstash Redis for instant search result retrieval.</li>
                <li style={{ marginBottom: '0.8rem' }}>• <strong>Frontend Interface:</strong> React 18, Vite, and Lucide Icons.</li>
            </ul>

            <div style={{ marginTop: '3rem', textAlign: 'center' }}>
                <a href="https://github.com/ripp3r-ds/BrahmiNet" target="_blank" rel="noopener noreferrer">
                    View the Source Code on GitHub
                </a>
            </div>
        </div>
    );
}
