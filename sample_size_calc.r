n.wilcox.ord(power = 0.8, 
             alpha = 0.05, 
             t = 0.50, 
             p = c(0.50, 0.25, 0.25),
             q = c(0.35, 0.325, 0.325));

n.wilcox.ord(power = 0.8, 
             alpha = 0.05, 
             t = 0.50,
             p = c(0.50, 0.25, 0.25),
             q = c(0.65, 0.175, 0.175));

n.wilcox.ord(power = 0.8, 
             alpha = 0.05,
             t = 0.53,
             p = c(0.15, 0.66, 0.19),
             q = c(0.23, 0.61, 0.16));

# In a standard survey to determine the coverage of immunization needed using 
# a cluster sampling technique on a population of approximately 500000, and
# an estimated prevalence of 70 percent, design effect is assumed to be 2.

n.for.survey( p = .8, delta = .05, popsize = 522000, deff =2) # 123 needed
n.for.2means(mu1 = 95, mu2 = 95, sd1=2, sd2=3)

#mu1, mu2= means of samples
#sd1,sd2 = std deviations

n.ttest(power = 0.8, alpha = 0.05, mean.diff = 0.80, sd1 = 0.83, sd2 =
          2.65, k = 0.001, design = "unpaired", fraction = "unbalanced", variance =
          "equal")