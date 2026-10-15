def test_gestor_con_datos_arranca_con_lo_esperado(gestor_con_datos):
    assert len(gestor_con_datos.clientes) == 2
    assert len(gestor_con_datos.rutas) == 3
    assert gestor_con_datos.buscar_pedido("PED-0001").estado == "pendiente"
