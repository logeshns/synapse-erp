export function getErrorMessage(error) {
  return error?.response?.data?.error?.message || error?.message || 'Something went wrong. Please try again.'
}