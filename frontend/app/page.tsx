import { redirect } from 'next/navigation'

export default function HomePage() {
  // Always redirect to login page first for proper authentication flow
  redirect('/login')
}
