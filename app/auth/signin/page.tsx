import SignInButton from "@/components/auth/SignInButton";

export default function SignInPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-md w-full space-y-8 p-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-extrabold text-gray-900 dark:text-white">
            Sign in to Interview Quotient
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Get AI-powered interview preparation with personalized coaching
          </p>
        </div>
        <div className="mt-8 space-y-6">
          <div className="flex justify-center">
            <SignInButton />
          </div>
          <div className="text-center text-xs text-gray-500 dark:text-gray-400">
            By signing in, you agree to our terms of service and privacy policy.
          </div>
        </div>
      </div>
    </div>
  );
}