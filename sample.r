is_even <- function(num) {
  if (num %% 2 == 0) {
    return(TRUE)
  } else {
    return(FALSE)
  }
}
print(is_even(10))