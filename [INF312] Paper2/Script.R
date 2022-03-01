library(tidyverse)
# Lists of datasets
lists_of_datasets <- tibble(`File Name of dataset` = c("fig_1.csv",
                              "fig_2e.csv",
                              "fig_5.csv",
                              "fig_6.csv",
                              "figs_1_2_3.csv",
                              "igs_2a_2b.csv",
                              "numberbirths_2001_2019.csv",
                              "births_educ_race_age6.csv",
                              "numbirths_educ_race_age6.csv",
                              "numbirths_educ_2044.csv",
                              "numbirths_hisp_nativity_mexican.csv"),
       `File Path` =  c("144981-V1/data",
                        "144981-V1/data",
                        "144981-V1/data",
                        "144981-V1/data",
                        "144981-V1/data",
                        "144981-V1/data",
                        "144981-V1/data/annual_policy",
                        "144981-V1/data/decomp",
                        "144981-V1/data/decomp",
                        "144981-V1/data/educ",
                        "144981-V1/data/hisp"))
lists_of_datasets$`File Name of dataset` <- str_replace_all(lists_of_datasets$`File Name of dataset`, ".csv", "")
  

lists_of_datasets |>
  knitr::kable(
    caption = "The List of datasets with File Path",
    col.names = c("File Name of dataset (.csv)", "File Path"),
    booktabs = TRUE,
    linesep = ""
  )

# Figure 1. Trend in US Birth Rates
# A. Graph
trend_us_br <- read_csv("fig_1.csv")
trend_us_br |>
  ggplot(aes(x = year, y = brate_all)) +
  geom_line(color = "blue") +
  labs(x = "", y = "Births per 1,000 women age 15-44", 
       caption = "Source: Birth Rates collected from CDC Vital Statistics Births Reports for 2015, 2019, and 2020. \n See Data Appendix for additional detials",
       title = "Trend in US Birth Rates") +
  scale_x_continuous(breaks = seq(1980, 2020, by = 5), 
                   labels = seq(1980, 2020, by = 5),
                   limits = c(1980, 2020)) +
  scale_y_continuous(breaks = seq(50, 80, by = 5),
                     labels = seq(50, 80, by = 5),
                     limits = c(50, 80)) +
  theme_classic()+
  theme(plot.margin = margin(0,0,0,0),
          line = element_line(colour = "gray"),
        text = element_text(size = 8, face = "plain"),
        title = element_text(size = 8, face = "bold"),
        axis.title.y = element_text(size = 8, face = "plain"),
        panel.grid.major.x = element_blank(),
        panel.grid.major.y = element_line(size = 0.1, color = "gray")) +
  geom_vline(xintercept = 2007, linetype= "dashed", color = "gray", show.legend = 2007) +
  geom_text(aes(x = 2010, y = 70, label = "2007"), 
            size = 2.5,
            fontface = "plain")
# B. Table
library(knitr)
peak_bottom_a <- trend_us_br |>
  filter(year %in% c(1990, 1997))

peak_bottom_b <- trend_us_br |>
  filter(year %in% c(2007, 2020))

rate_comparison <- tibble(
  Period = c("1990-1997", "2007-2020"),
  'Decrease Rate (%)' = c((peak_bottom_a[2,2] - peak_bottom_a[1,2])*100/(peak_bottom_a[1,2]),
                      (peak_bottom_b[2,2] - peak_bottom_b[1,2])*100/(peak_bottom_b[1,2]))
)

rate_comparison |>
  knitr::kable(
  caption = "Changes in Births per 1,000 women age 15-44 from 1990-1997 to 2007-2020",
  gitis = 3,
  booktabs = TRUE,
  linesep = "")

# Figure 2.Trends in Birth Rates by Population Subgroup
# A. Five-year age group
trend_us_sg <- read_csv("figs_2a_2b.csv")
trend_us_agegroup <- trend_us_sg |>
  select(1:7)
trend_us_agegroup <- trend_us_agegroup |>
  pivot_longer(cols = 2:7, names_to = "agegroup", values_to = "birth_rate")


text_y_lists <- c(53.0,
                  115.1,
                  112.9,
                  61.9,
                  19.8,
                  3.9)  
text_y_lists <- text_y_lists + 3

trend_us_agegroup_table <- trend_us_agegroup |>
  filter(year %in% c(2007,2020)) |>
  pivot_wider(id_cols = c("agegroup", "birth_rate"),
              names_from = "year",
              values_from = "birth_rate") |>
  summarize(agegroup = str_replace_all(agegroup,"brate_", "Age " ),
            rate = (`2020`-`2007`)*100/`2007`)


trend_us_agegroup |>
  ggplot(aes(x = year, y = birth_rate, color = agegroup)) +
  geom_line() +
  labs(x = "", y = "Births per 1,000 women in \n relevant population subgroup",
       title =  "Trends in Birth Rates for Five-year age group") +
  scale_x_continuous(breaks = seq(1980, 2020, by = 5),
                     labels = seq(1980, 2020, by = 5),
                     limits = c(1980, 2020)) +
  scale_y_continuous(breaks = seq(0, 140, by = 20),
                    labels = seq(0, 140, by = 20),
                    limits = c(0, 140)) +
  theme_classic() +
  theme(plot.margin = margin(0,0,0,0),
        line = element_line(colour = "gray"),
        text = element_text(size = 8, face = "plain"),
        title = element_text(size = 8, face = "bold"),
        axis.title.y = element_text(size = 8, face = "plain"),
        panel.grid.major.x = element_blank(),
        panel.grid.major.y = element_line(size = 0.1, color = "gray"),
        legend.position = "none") +
  geom_vline(xintercept = 2007, linetype= "dashed", color = "gray", show.legend = 2007) +
  geom_text(aes(x = 2010, y = 120, label = "2007"), 
            size = 2.5,
            fontface = "plain",
            colour = "black") +
  geom_text(aes(x = 1982, y = text_y_lists[1], label = "Age 15-19"),
            size = 2.5,
            fontface = "plain",
            colour = "black") +
  geom_text(aes(x = 1982, y = text_y_lists[2]-14, label = "Age 20-24"),
            size = 2.5,
            fontface = "plain",
            colour = "black") +
  geom_text(aes(x = 1982, y = text_y_lists[3], label = "Age 25-29"),
            size = 2.5,
            fontface = "plain",
            colour = "black") +
  geom_text(aes(x = 1982, y = text_y_lists[4], label = "Age 30-34"),
            size = 2.5,
            fontface = "plain",
            colour = "black") +
  geom_text(aes(x = 1982, y = text_y_lists[5], label = "Age 35-39"),
            size = 2.5,
            fontface = "plain",
            colour = "black") +
  geom_text(aes(x = 1982, y = text_y_lists[6], label = "Age 40-44"),
            size = 2.5,
            fontface = "plain",
            colour = "black")

trend_us_agegroup_table |>
  knitr::kable(
    caption = "Changes in Births per 1,000 women age 15-44 from 2007 to 2020 by age group",
    col.names = c("Age Group", "Change Rate (%)"),
    gitis = 3,
    booktabs = TRUE,
    linesep = "")

# B. Race and ethnicity (age 15-44)
trend_us_race_ethnicity <- trend_us_sg |>
  select(c(1, 8:10))

trend_us_race_ethnicity <- trend_us_race_ethnicity |>
  filter(is.na(brate_hisp)==FALSE)

trend_us_race_ethnicity <-
  trend_us_race_ethnicity |>
  pivot_longer(cols = 2:4, names_to = "ethnicity_group", values_to = "birth_rate")

trend_us_race_ethnicity |>
  filter(year == 1995)
text_y_lists_2 <- c(57.5, 72.8, 98.8)
text_y_lists_2 <- text_y_lists_2 +3

trend_us_race_ethnicity |>
  ggplot(aes(x = year, y = birth_rate, colour = ethnicity_group)) +
  geom_line() +
  labs(x = "", y = "Births per 1,000 women in \n relevant population subgroup",
       title = "Trends in Birth Rates by Race and Ethnicity (ages 15-44)") +
  scale_x_continuous(breaks = seq(1990, 2020, by = 5),
                    labels = seq(1990, 2020, by = 5),
                    limits = c(1990, 2020)) +
  scale_y_continuous(breaks = seq(0, 140, by = 20),
                    labels = seq(0, 140, by = 20),
                    limits = c(0, 140)) +
  theme_classic() +
  theme(plot.margin = margin(0,0,0,0),
        line = element_line(colour = "gray"),
        text = element_text(size = 8, face = "plain"),
        title = element_text(size = 8, face = "bold"),
        axis.title.y = element_text(size = 8, face = "plain"),
        panel.grid.major.x = element_blank(),
        panel.grid.major.y = element_line(size = 0.1, color = "gray"),
        legend.position = "none")+
  geom_vline(xintercept = 2007, linetype= "dashed", color = "gray", show.legend = 2007) +
  geom_text(aes(x = 2010, y = 137, label = "2007"), 
            size = 2.5,
            fontface = "plain",
            colour = "black") +
  geom_text(aes(x = 2000, y = text_y_lists_2[1]-7, label = "White, non-Hispanic"),
            size = 2.5,
            fontface = "plain",
            colour = "black") +
  geom_text(aes(x = 2000, y = text_y_lists_2[2]+2, label = "Black, non-Hispanic"),
            size = 2.5,
            fontface = "plain",
            colour = "black") +
  geom_text(aes(x = 2000, y = text_y_lists_2[3]+2, label = "Hispanic"),
            size = 2.5,
            fontface = "plain",
            colour = "black") 


# Change in Birth Rates by State, 2004-2008 to 2015-2019
change_br_by_state <- read_csv("numbirths_2001_2019.csv")
change_br_by_state <- change_br_by_state |>
  filter(year %in% c(2004:2008, 2015:2019))
change_br_by_state <- change_br_by_state |>
  mutate(period = case_when(
    year>=2004 & year <=2008 ~ "2004-2008",
    year >2009 ~ "2015-2019"))
change_br_by_state_cleaned <- change_br_by_dfstate |>
  group_by(stname, period) |>
  summarize(averge= mean(numbirth1544))
view(change_br_by_state)
view(change_br_by_state_cleaned)
change_br_by_state_period_1 <- change_br_by_state_cleaned |>
  filter(period == "2004-2008")
change_br_by_state_period_2 <- change_br_by_state_cleaned |>
  filter(period == "2015-2019")

change_br_by_state_updated <- change_br_by_state_period_1 |>
  cbind(change_br_by_state_period_2$period, change_br_by_state_period_2$averge)
colnames(change_br_by_state_updated) <- c("state", "period_1", "average_1", "period_2", "average_2")

change_br_by_state_final <- change_br_by_state_updated |>
  mutate(rate = (average_2 - average_1)/average_1 *100) |>
  select(state, rate) |>
  mutate(rate_category = case_when(
    rate > 0 ~ "> 0",
    rate > -5 & rate <=0 ~ "0 to -5",
    rate > -10 & rate <=-5 ~ "-5 to -10",
    rate <= -10 ~ "< -10"
  ))
view(change_br_by_state_final)

change_br_state_data <- read_csv("fig_7.csv")
colnames(change_br_state_data) <- c("state", "rate")
change_br_state_data <- change_br_state_data |>
  mutate(rate_category = case_when(
    rate > 0 ~ "> 0",
    rate > -5 & rate <=0 ~ "0 to -5",
    rate > -10 & rate <=-5 ~ "-5 to -10",
    rate <= -10 ~ "< -10"
  ))

# install.packages("usmap")
library(usmap)
plot_usmap(data = change_br_state_data, values = "rate_category", regions = "states") +
  labs(title = "Change in Birth Rates by State, 2004-2008 to 2015-2019",
       caption = "Source: Birth data are from NCHS Vital Statistics. \n Population data are from CDC sruveillance, Epidemiology, and End Results (SEER) program. \n Note: Birth rates are calculated among women aged 15 to 44") +
  theme(panel.background=element_blank(),
        title = element_text(face = "bold"),
        text = element_text(face = "plain"),
        legend.position = "right") +
  scale_fill_manual(values = c("> 0" = "white", 
                               "0 to -5" = "yellow",
                               "-5 to -10" = "orange",
                               "< -10" = "red"),
                    name = "Change in birth rate")


# Hispanic data
hispanic_data <- read_csv("hispanic.csv")
hispanic_data <- hispanic_data |>
  mutate(hispanic_total_rate = (WhiteHispanicPerc + BlackHispanicPerc + AsianHispanicPerc + HawaiianHispanicPerc + IndianHispanicPerc + OtherHispanicPerc)*100)
hispanic_data <- hispanic_data |>
  select(State, hispanic_total_rate) |>
  arrange(desc(hispanic_total_rate))

head(hispanic_data, n = 5) |>
  knitr::kable(col.names = c("State Name", "Hispanic Percentage (%)"),
               caption = "The percentage of hispanic population by each state",
               gitis = 3,
               booktabs = TRUE,
               linesep = "")
