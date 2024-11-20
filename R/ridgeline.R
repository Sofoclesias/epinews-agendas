library(ggplot2)
library(ggridges)
library(viridis)

# Load your data
data <- read.csv("D:/Repos/Universidad/discursos-enfermedades/R/enf.csv")

# Convert year to factor for proper ordering
data$AÑO <- as.factor(data$AÑO)  # Convert years to factors
data$SEMANA <- as.numeric(data$SEMANA)  # Ensure weeks are numeric

# Create the ridgeline plot
ggplot(data, aes(x = SEMANA, y = AÑO, fill = CATEGORIA)) +
  geom_density_ridges(
    scale = 3,                    # Adjust height scaling
    rel_min_height = 0.01,        # Minimal height for density ridges
    alpha = 0.8                   # Transparency of filled areas
  ) +
  scale_fill_viridis_d(
    name = "Category",            # Legend title
    option = "plasma"             # Color palette
  ) +
  labs(
    title = "Ridgeline Plot of Weekly Data by Year and Category",
    x = "Week",
    y = "Year"
  ) +
  theme_ridges() +
  theme(
    plot.title = element_text(size = 16, face = "bold"),
    axis.title.x = element_text(size = 12),
    axis.title.y = element_text(size = 12),
    legend.position = "right"
  )