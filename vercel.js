// For Vercel deployment - detect the Vercel platform
if (process.env.VERCEL || process.env.VERCEL_ENV) {
  console.log('Vercel deployment detected. Environment:');
  console.log('- VERCEL:', process.env.VERCEL);
  console.log('- VERCEL_ENV:', process.env.VERCEL_ENV);
  console.log('- NODE_ENV:', process.env.NODE_ENV);
  
  // Configure for Vercel
  process.env.IS_VERCEL = 'true';
}
