// To support your Dynamic Branding goal, we need to extend Tailwind to use CSS variables./** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // These will be populated by the TenantProvider later
                brand: {
                    primary: 'var(--brand-primary)',
                    secondary: 'var(--brand-secondary)',
                    accent: 'var(--brand-accent)',
                }
            },
        },
    },
    plugins: [],
}