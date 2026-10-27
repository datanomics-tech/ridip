import Nav from "./Nav";
import { Link, useLocation } from "./router";
import About from "./pages/About";
import Compare from "./pages/Compare";
import Explore from "./pages/Explore";
import Home from "./pages/Home";
import OpenInnovation from "./pages/OpenInnovation";
import Place from "./pages/Place";
import Report from "./pages/Report";

const TRACKS = {
  "/finance-poverty": "finance_poverty",
  "/agriculture": "agriculture",
  "/open-innovation/employment": "employment",
  "/open-innovation/health": "health",
  "/open-innovation/education": "education",
  "/open-innovation/transport": "transport",
} as const;

export default function App() {
  const { path, params } = useLocation();
  const clean = path.replace(/\/+$/, "") || "/";

  let page;
  if (clean === "/") page = <Home />;
  else if (clean === "/open-innovation") page = <OpenInnovation />;
  else if (clean === "/explore") page = <Explore basePath="/explore" indicator={params.get("i")} year={params.get("y")} place={params.get("place")} />;
  else if (clean in TRACKS) {
    const domain = TRACKS[clean as keyof typeof TRACKS];
    page = <Explore key={domain} domain={domain} basePath={clean} indicator={params.get("i")} year={params.get("y")} place={params.get("place")} />;
  } else if (clean.startsWith("/place/")) page = <Place code={clean.slice(7)} tab={params.get("tab") ?? "overview"} />;
  else if (clean === "/compare") page = <Compare a={params.get("a")} b={params.get("b")} />;
  else if (clean === "/reports/new") page = <Report place={params.get("place")} compare={params.get("compare")} />;
  else if (clean === "/about") page = <About />;
  else page = <main className="page"><h1>Page not found</h1><Link to="/">Go to the home page</Link></main>;

  return (
    <div className="layout">
      <Nav />
      {page}
    </div>
  );
}
