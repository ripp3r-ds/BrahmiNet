export default function About() {
    return (
        <div className="page-container">
            <h2 className="gradient-text">About BrahmiNet</h2>

            <p>
                Welcome to <strong>BrahmiNet</strong>, an exclusive, production-grade
                Agentic AI system dedicated to curating and retrieving the finest Telugu memes,
                with a special focus on the legendary Brahmanandam Garu.
            </p>

            <p>
                <strong>How it works:</strong> BrahmiNet doesn't just look at text tags.
                It utilizes cutting-edge Vision LLMs to literally "watch" the memes as they are ingested.
                It understands the exact dialogue written, the raw emotion on Brahmi's face,
                the film it's from, and the specific life situation it perfectly reacts to.
            </p>

            <p>
                All of this rich context is converted into heavy semantic embeddings, stored in a
                high-performance PostgreSQL vector database, and cached on the edge using Upstash Redis.
            </p>

            <p>
                Stop scrolling endlessly for the perfect reaction. Just search for how you feel,
                and let the AI deliver the perfect Brahmi expression.
            </p>
        </div>
    );
}
