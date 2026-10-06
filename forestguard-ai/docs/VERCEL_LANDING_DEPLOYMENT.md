# Deploy the public landing page to Vercel

This deploys the public React/Vite landing page only. The officer dashboard, login API, local database, and saved analysis files are not hosted by this setup. On the deployed site, the Officer Login button explains that sign-in is available in the local workspace. The local demo keeps its existing sign-in flow.

## 1. Push the project to GitHub

1. Commit and push this project to a GitHub repository you control. The Vercel Git integration can use a private repository.
2. Check that `frontend/package.json`, `frontend/pnpm-lock.yaml`, and `frontend/src/` are committed. Do not add `.env` files, credentials, local databases, or imagery/model files.

## 2. Create the Vercel project

1. Sign in to [Vercel](https://vercel.com/) and choose **Add New → Project**.
2. Import the GitHub repository containing ForestGuard AI.
3. Set **Root Directory** to `frontend` and confirm that the selected folder contains `package.json`.
4. Use the Vite framework preset and these build settings:
   - Install Command: `pnpm install --frozen-lockfile`
   - Build Command: `pnpm run build`
   - Output Directory: `dist`
5. The Vite build detects Vercel's `VERCEL=1` system variable and automatically builds the public landing-page mode. If system environment variables are disabled in Vercel, add `VITE_FORESTGUARD_LANDING_ONLY=true` under **Environment Variables** for Production, Preview, and Development.
6. Choose **Deploy**. Vercel builds the static site and gives you a `vercel.app` URL. Later pushes to the connected branch create new deployments.

The optional variable is intentionally named with Vite's `VITE_` prefix because it is a public build setting, not a secret. Hosted mode contains no local password or login form and does not send a login request to a missing API.

## 3. Check the deployed page

Open the deployment URL and check the hero animation, navigation links, FAQ, mobile layout, and reduced-motion behavior. Select **Officer login**: it should show the local-workspace notice and return to the landing page. A Vercel deployment of this static page cannot sign an officer in or load the locally stored dashboard.

If a setting was changed after deployment, create a new deployment so Vercel rebuilds with the updated environment variables. To update the page, push a commit to the connected Git branch.

## Cost and account note

Vercel's Hobby plan is currently free for personal, non-commercial projects, subject to plan limits. Check Vercel's current plan terms before deploying or sharing it as an operational service. Do not start a paid trial or upgrade if maintaining the ₹0 constraint.
