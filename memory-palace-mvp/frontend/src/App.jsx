import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import WordInput from './pages/WordInput'
import Scene from './pages/Scene'
import Admin from './pages/Admin'

function App() {
  return (
    <div className="min-h-screen">
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/create" element={<WordInput />} />
        <Route path="/scene/:id" element={<Scene />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  )
}

export default App
