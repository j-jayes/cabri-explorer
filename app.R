library(shiny)
library(tidyverse)
library(readxl)
library(DT)

data_raw <- read_excel("document_links_1.xlsx") %>%
  as_tibble() %>%
  mutate(CycleDocument = paste(`Cycle phase`, `Document type`, sep = ": "),
         `Document type short` = str_squish(str_extract(`Document type`, "^[^\\-]*")),
         CycleDocumentShort = paste(`Cycle phase`, `Document type short`, sep = ": ")) %>%
  dplyr::filter(!is.na(Country)) %>%
  mutate(Year = parse_number(Year))


# test_table <- data_raw %>%
#   filter(Country == "South Africa") %>%
#   count(Year, CycleDocument) %>%
#   pivot_wider(names_from = Year, values_from = n, values_fill = 0)



ui <- fluidPage(
  selectInput("countryInput", "Choose a country:",
              choices = ""),
  dataTableOutput("table")
)

server <- function(input, output, session) {

  observe({
    updateSelectInput(session, "countryInput",
                      choices = unique(data_raw$Country))
  })

  output$table <- renderDataTable({
    req(input$countryInput)

    # Filter data for selected country
    filtered_data <- data_raw %>%
      filter(Country == input$countryInput) %>%
      count(Year, CycleDocumentShort) %>%
      arrange(Year)

    n_rows <- filtered_data %>% count() %>% pull()

    # Wide data
    wide_data <- filtered_data %>%
      pivot_wider(names_from = Year, values_from = n, values_fill = 0) %>%
      arrange(CycleDocumentShort)

    # Formatting datatable
    datatable(wide_data, options = list(dom = 't', pageLength = n_rows))
  })
}

shinyApp(ui = ui, server = server)

