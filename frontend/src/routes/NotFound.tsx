import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-hanyang-cream">
      <div className="text-center">
        <h1 className="font-display text-6xl text-hanyang-navy mb-4">404</h1>
        <p className="text-xl text-hanyang-stone mb-8">
          페이지를 찾을 수 없습니다
        </p>
        <Link to="/" className="btn-primary">
          홈으로 돌아가기
        </Link>
      </div>
    </div>
  )
}
