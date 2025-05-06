import requests
from datetime import date


def get_url(year):
    return f"https://nolaborables.com.ar/api/v2/feriados/{year}"


months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
days = ['Lunes', 'Martes',
        'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']


def day_of_week(day, month, year):
    return days[date(year, month, day).weekday()]


class NextHoliday:
    def __init__(self):
        self.loading = True
        self.year = date.today().year
        self.holiday = None
        self.type = None

    def set_next(self, holidays, type):
        now = date.today()
        today = {
            'day': now.day,
            'month': now.month
        }

        holiday = next(
            (h for h in holidays if (h['mes'] == today['month'] and h['dia'] >
                                     today['day'] or h['mes'] > today['month'])
             and (type == None or h['tipo'] == type)), holidays[0]
        )

        self.loading = False
        self.holiday = holiday

    def fetch_holidays(self):
        response = requests.get(get_url(self.year))
        data = response.json()
        self.set_next(data, self.type)

    def render(self):
        if self.loading:
            print("\nBuscando...")
        else:
            if self.type == None:
                print("\nPróximo feriado: " + self.holiday['motivo'])
            else:
                print("\nPróximo feriado de tipo " +
                      self.type + ": " + self.holiday['motivo'])
            print("Fecha: " + day_of_week(self.holiday['dia'],
                                          self.holiday['mes'], self.year)
                  + " " + str(self.holiday['dia']) + " de "
                  + months[self.holiday['mes'] - 1])
            print("Tipo: " + self.holiday['tipo'].capitalize() + "\n")


if __name__ == '__main__':
    next_holiday = NextHoliday()
    input_user = 0
    while input_user != 1 and input_user != 2:
        input_user = int(input(
            "Seleccione una opción: 1: Próximo feriado, " +
            "2: Próximo feriado por tipo, 3: Terminar programa\n"))
        if input_user == 1:
            next_holiday.fetch_holidays()
            next_holiday.render()
            input_user == 3
        elif input_user == 2:
            while next_holiday.type not in ['inamovible', 'trasladable',
                                            'nolaborable', 'puente']:
                next_holiday.type = input(
                    "\nSeleccione el tipo de feriado a buscar: inamovible, " +
                    "trasladable, nolaborable o puente\n")
            next_holiday.fetch_holidays()
            next_holiday.render()
            next_holiday.type = None
        elif input_user == 3:
            break
        else:
            print("Opción incorrecta\n")
