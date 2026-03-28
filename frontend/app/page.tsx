import Link from "next/link";

export default function HomePage() {
  return (
    <div className="marketingShell">
      <header className="marketingHeader">
        <Link href="/" className="portalBrand">
          HLGS
        </Link>
        <div className="actions">
          <Link href="/login">Open portals</Link>
        </div>
      </header>

      <section className="heroStage">
        <div className="heroCopy">
          <p className="eyebrow">Human-Like Grading System</p>
          <h1>An academic grading platform built for teachers, students, and parents.</h1>
          <p className="portalLead">
            Teachers create and assign assessments, students answer in a focused workspace, and parents receive readable progress reports.
          </p>
          <div className="actions">
            <Link href="/login">Enter demo portals</Link>
            <Link href="/teacher" className="secondary">
              Teacher portal
            </Link>
          </div>
        </div>

        <div className="heroPanelLarge">
          <div className="panelList">
            <div className="listCard">
              <strong className="listTitle">Teacher</strong>
              <p className="muted">Author assessments, import textbook PDFs, assign work, and audit full grading logic.</p>
            </div>
            <div className="listCard">
              <strong className="listTitle">Student</strong>
              <p className="muted">Complete assigned answers in an exam-style screen and see clear, encouraging feedback.</p>
            </div>
            <div className="listCard">
              <strong className="listTitle">Parent</strong>
              <p className="muted">Follow academic progress through plain-language reports and downloadable PDFs.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="statStrip">
        <div className="statCard">
          <p className="cardLabel">Scoring model</p>
          <div className="statValue">4 layers</div>
          <p className="muted">Keywords, semantics, cognitive depth, and weighted teacher-style judgment.</p>
        </div>
        <div className="statCard">
          <p className="cardLabel">Portal structure</p>
          <div className="statValue">3 roles</div>
          <p className="muted">Teacher, student, and parent journeys built on one shared grading engine.</p>
        </div>
        <div className="statCard">
          <p className="cardLabel">Hackathon fit</p>
          <div className="statValue">Live demo ready</div>
          <p className="muted">Mock sessions and seeded users make the product easy to demonstrate quickly.</p>
        </div>
      </section>
    </div>
  );
}
