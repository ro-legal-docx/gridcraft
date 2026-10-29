//! Cells show numbers and dates in the display region (`Session::display_locale`): its
//! separators for a format's `.` and `,`, its short date for the built-in date format. The
//! values, codes and everything outside the grid stay en-US.

use egui::Shape;
use gridcraft_engine::Session;
use gridcraft_engine::numfmt::Locale;
use gridcraft_ui_egui::SheetApp;
use serde_json::json;

type Harness = egui_kittest::Harness<'static, SheetApp>;

fn harness(tag: Option<&str>) -> Harness {
    let mut s = Session::new();
    s.new_workbook();
    s.execute("range.setValues", json!({"range": "A1:A3", "values": [[1169.5], [45292], [0.25]]})).unwrap();
    s.execute("home.formatCells", json!({"range": "A1", "style": {"num_fmt": "#,##0.00"}})).unwrap();
    s.execute("home.formatCells", json!({"range": "A2", "style": {"num_fmt": "m/d/yyyy"}})).unwrap();
    // Wide enough for every form, so none turns into ####.
    s.execute("home.columnWidth", json!({"cols": "A:A", "chars": 20})).unwrap();
    s.execute("selection.set", json!({"range": "H20"})).unwrap();
    let mut app = SheetApp::new(s, Default::default());
    if let Some(tag) = tag {
        app.session.display_locale = Locale::from_tag(tag);
    }
    let mut h = egui_kittest::Harness::builder().with_size(egui::vec2(1200.0, 800.0)).build_ui_state(
        |ui, app: &mut SheetApp| {
            app.logic(ui.ctx());
            app.ui(ui);
        },
        app,
    );
    h.run_steps(4);
    h
}

fn painted(h: &Harness, text: &str) -> bool {
    h.output().shapes.iter().any(|s| matches!(&s.shape, Shape::Text(t) if t.galley.job.text == text))
}

#[test]
fn swiss_region_shows_apostrophe_groups_and_dotted_dates() {
    let h = harness(Some("en_CH"));
    assert!(painted(&h, "1'169.50"));
    assert!(painted(&h, "01.01.2024"));
    assert!(painted(&h, "0.25"));
    // The stored code and value are unchanged.
    let d = h.state().session.active().unwrap();
    let sh = d.wb.active().unwrap();
    assert_eq!(d.wb.styles.get(sh.style_id(gridcraft_engine::core::CellRef::new(1, 0))).num_fmt.as_str(), "m/d/yyyy");
}

#[test]
fn german_region_shows_decimal_commas() {
    let h = harness(Some("de-DE"));
    assert!(painted(&h, "1.169,50"));
    assert!(painted(&h, "01.01.2024"));
    assert!(painted(&h, "0,25"));
}

#[test]
fn default_region_is_en_us() {
    let h = harness(None);
    assert!(painted(&h, "1,169.50"));
    assert!(painted(&h, "1/1/2024"));
}

#[test]
fn romanian_region_shows_grouped_numbers_and_dates() {
    let h = harness(Some("ro-RO"));
    assert!(painted(&h, "1.169,50"));
    assert!(painted(&h, "01.01.2024"));
    assert!(painted(&h, "0,25"));
}

#[test]
fn system_custom_short_date_and_literal_custom_code_paint_differently() {
    let mut h = harness(Some("en_US@rg=sgzzzz"));
    h.state_mut().session.display_locale = Locale::from_tag("en_US@rg=sgzzzz").with_icu_short_date("dd.MM.y");
    let doc = h.state_mut().session.active_mut().unwrap();
    let wb = std::sync::Arc::make_mut(&mut doc.wb);
    let style = wb.styles.derive(Default::default(), |st| st.num_fmt = gridcraft_engine::model::NumFmt::custom("m/d/yyyy"));
    let sh = wb.sheet_mut(0).unwrap();
    sh.cells.set(
        gridcraft_engine::core::CellRef::new(3, 0),
        gridcraft_engine::model::Cell { value: gridcraft_engine::core::Value::Number(45292.0), formula: None, style },
    );
    h.run_steps(4);
    assert!(painted(&h, "01.01.2024"));
    assert!(painted(&h, "1/1/2024"));
}
