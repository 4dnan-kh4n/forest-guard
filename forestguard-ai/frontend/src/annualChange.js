export function annualChange(change) {
  if (!change || !Number.isFinite(change.common_pixels) || change.common_pixels <= 0) return null;
  const counts = change.transition_pixels;
  if (!counts || [0,1,2,3].some(code => !Number.isInteger(counts[code]) || counts[code] < 0) || Object.values(counts).reduce((a,b)=>a+b,0) !== change.common_pixels) return null;
  const netPixels = counts[3] - counts[2];
  return {direction:netPixels < 0 ? 'decreased' : netPixels > 0 ? 'increased' : 'unchanged',
    netHa:Math.abs(netPixels)*0.04,
    beforePercent:100*(counts[1]+counts[2])/change.common_pixels,
    afterPercent:100*(counts[1]+counts[3])/change.common_pixels};
}
