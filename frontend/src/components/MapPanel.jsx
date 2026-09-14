import { useEffect, useState } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
  ZoomableGroup,
} from "react-simple-maps";
import shp from "shpjs";
import world from "world-atlas/countries-110m.json";

const countryByNumericId = {"156":"CHN","360":"IDN","704":"VNM","076":"BRA","484":"MEX","710":"ZAF","566":"NGA","050":"BGD","608":"PHL","840":"USA","826":"GBR","276":"DEU","392":"JPN","250":"FRA","124":"CAN","036":"AUS"};
const colorByCountry = {CHN:"#e2352e",IDN:"#f0a000",VNM:"#169653",BRA:"#14a5a5",MEX:"#c96845",ZAF:"#d45791",NGA:"#855a35",BGD:"#4f944d",PHL:"#8968bf",USA:"#7456c8",GBR:"#425e92",DEU:"#6c7b91",JPN:"#956169",FRA:"#7550a8",CAN:"#af5757",AUS:"#5068a8"};

export function MapPanel({ selected }) {
  const [india, setIndia] = useState(null);
  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}maps/survey-of-india-outline.zip`)
      .then((response) => response.arrayBuffer())
      .then(shp)
      .then((data) => setIndia(Array.isArray(data) ? data[0] : data))
      .catch(() => setIndia(null));
  }, []);
  return (
    <article className="map-card panel">
      <h2>World comparison</h2>
      <div
        className="map-wrap"
        role="img"
        aria-label="World map highlighting selected comparison countries"
      >
        <ComposableMap
          projectionConfig={{ scale: 132 }}
          width={420}
          height={190}
        >
          <ZoomableGroup center={[10, 12]} zoom={1}>
            <Geographies geography={world}>
              {({ geographies }) =>
                geographies.map((geo) => {
                  const id = String(geo.id).padStart(3, "0");
                  if (id === "356") return null;
                  const code = countryByNumericId[id] || "";
                  return (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      fill={selected.includes(code) ? colorByCountry[code] : "#dce2ea"}
                      stroke="#f8fafc"
                      strokeWidth={0.35}
                      style={{
                        default: { outline: "none" },
                        hover: {
                          fill: selected.includes(code)
                            ? colorByCountry[code]
                            : "#cbd5e1",
                          outline: "none",
                        },
                        pressed: { outline: "none" },
                      }}
                    />
                  );
                })
              }
            </Geographies>
            {india && (
              <Geographies geography={india}>
                {({ geographies }) =>
                  geographies.map((geo) => (
                    <Geography
                      key={geo.rsmKey}
                      geography={geo}
                      fill={selected.includes("IND") ? "#1467d9" : "#dce2ea"}
                      stroke="#fff"
                      strokeWidth={0.35}
                    />
                  ))
                }
              </Geographies>
            )}
          </ZoomableGroup>
        </ComposableMap>
      </div>
      <p>Selected countries are highlighted.</p>
    </article>
  );
}
