import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { LiveEvents } from './pages/LiveEvents';
import { Services } from './pages/Services';
import { Analytics } from './pages/Analytics';
import { Playground } from './pages/Playground';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<LiveEvents />} />
          <Route path="services" element={<Services />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="playground" element={<Playground />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
